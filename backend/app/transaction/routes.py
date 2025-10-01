import json 
from flask_cors import CORS, cross_origin
from flask import Blueprint, request, jsonify, abort, make_response, g
from app.security import roles, permissions
from app.common import filters

from .service import TransactionService

__uri__ = 'transactions'
__blueprint__ = 'transactions'

transactions = Blueprint(__uri__, __name__)

service = TransactionService()

@transactions.route('/', methods=['GET'])
#@cross_origin()
#@permissions.has_permission(['transaction.show'])
@roles.token_required
@filters.filters
def get_all_transactions(filter,self):
    transactions, status = service.get_transactions(None,filter)
    return jsonify(transactions), status

@transactions.route('/<id>', methods=['GET'])
#@cross_origin()
#@permissions.has_permission(['transaction.show'])
@roles.token_required
@filters.filters
def get_transaction(filter,self, id):
    transactions, status = service.get_transactions(id, filter)
    return jsonify(transactions), status

@transactions.route('/', methods=['POST'])
#@cross_origin()
#@permissions.has_permission(['transaction.add'])
def add_transaction():
    if not request.json:
        abort(404)
    message, status = service.create_transaction(request.json)
    return jsonify({'msg': message}), status

@transactions.route('/<id>', methods=['PATCH'])
#@cross_origin()
#@permissions.has_permission(['transaction.edit'])
@roles.token_required
def update_transaction(self,id):
    if not request.json:
        abort(404)
    message, status = service.update_transaction(id,request.json)
    return jsonify({'msg': message}), status


@transactions.route('/<id>', methods=['DELETE'])
#@cross_origin()
#@permissions.has_permission(['transaction.delete'])
@roles.token_required
def delete_transaction(self, id):
    message, status = service.delete_transaction(id)
    return jsonify({'msg': message}), status