from flask_cors import CORS, cross_origin
from flask import Blueprint, request, jsonify, abort, g, current_app
from app.common.queries import create_filters
from app.security import roles, permissions
from app.common import filters
from app.utilities.common_utils import equal_to, get_owner_id
from .service import QuotationService


__uri__ = 'quotations'
__blueprint__ = 'quotations'

quotations = Blueprint(__uri__, __name__)

service = QuotationService()

@quotations.route('/', methods=['GET'])
@roles.token_required
@filters.filters
def get_all_quotations(filter,self):
    response, status = service.get_quotations(None,filter)
    return jsonify({'quotations': response}), status

@quotations.route('/<id>', methods=['GET'])
#@cross_origin()
@roles.token_required
def get_quotation_by_id(self, id):
    #response, status = service.get_quotations_by_id(id)
    response, status = service.get_quotations(id, None)
    return jsonify({'quotations': response}), status

@quotations.route('/transaction/<transaction_id>', methods=['GET'])
#@cross_origin()
@roles.token_required
def get_quotation_by_transaction_id(self, transaction_id):
    response, status = service.get_quotations_by_transaction_id(transaction_id)
    if 'quotations.show.my' in g.permission:
        if not equal_to(response['user_id'], self.id):
            abort(403)
    return jsonify({'quotations': response}), status

# get_quotations_by_user_id
@quotations.route('/user/<user_id>', methods=['GET'])
#@cross_origin()
@roles.token_required
@filters.filters
def get_quotations_by_user_id(filter,self, user_id):
    response, status = service.get_quotations_by_user_id(user_id,filter)
   
    return jsonify({'quotations': response}), status
"""
@quotations.route('/customer_mobile/<mobile>', methods=['GET'])
@roles.token_required
@filters.filters
def get_quotations_by_customer_mobile(filter, self, mobile):
    response, status = service.get_quotations_by_customer_mobile(mobile, filter)
    return jsonify({'quotations': response}), status
"""
@quotations.route('/', methods=['POST'])
#@cross_origin()
@roles.token_required
def add_quotation(self):
    if not request.json:
        abort(400)
    response, status, id = service.create_quotation(request.json)
    return jsonify({'status': response, 'id': id}), status

@quotations.route('/return/', methods=['POST'])
#@cross_origin()
@roles.token_required
def create_quotation_refund(self):
    if not request.json:
        abort(400)
    response, status, id = service.create_quotation_refund(request.json)
    return jsonify({'status': response, 'id': id}), status

@quotations.route('/<id>', methods=['PATCH'])
#@cross_origin()
@roles.token_required
def update_quotation(self, id):
    message, status = service.update_quotation(id, request.json)
    return jsonify({'msg': message}), status

@quotations.route('/<id>', methods=['DELETE'])
#@cross_origin()
@permissions.has_permission(['quotations.delete'])
def delete_quotation(self, id):
    message, status = service.delete_quotation(id)
    return jsonify({'msg': message}), status

@quotations.route('/model/<model_type>', defaults={'model_id': None})
@quotations.route('/model/<model_type>/<model_id>', methods=['GET'])
#@cross_origin()
@roles.token_required
@filters.filters
def get_quotation_by_type_and_id_and_filter(filter,self,model_type=None, model_id=None):
    """
    
    if 'quotations.show.my' in g.permission:
        if filter.queries is not None:
            filter.queries.append('user_id,eq,'+str(get_owner_id()))
        else:
            filter.queries = ['user_id,eq,'+str(get_owner_id())]
        filter.filters = create_filters(filter.queries)
    """
    response, status = service.get_quotation_by_type_and_id_and_filter(model_type,model_id,filter)
    return jsonify({'quotations': response}), status