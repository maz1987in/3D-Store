import json 
from flask_cors import CORS, cross_origin
from flask import Blueprint, request, jsonify, abort, make_response, g
from app.security import roles, permissions
from app.common import filters
from app.utils.response import APIResponse
from app.decorators.validation import validate_json
from .schemas import TransactionCreateSchema, TransactionUpdateSchema

from .service import TransactionService

__uri__ = 'transactions'
__blueprint__ = 'transactions'

transactions = Blueprint(__uri__, __name__)

service = TransactionService()

@transactions.route('/', methods=['GET'])
#@cross_origin()
@permissions.has_permission(['transaction.show'])
@filters.filters
def get_all_transactions(self, filter):
    transactions, status = service.get_transactions(None, filter)
    if status == 200:
        return APIResponse.success(transactions, "Transactions retrieved successfully")
    return APIResponse.error("Failed to retrieve transactions", status_code=status)

@transactions.route('/<id>', methods=['GET'])
#@cross_origin()
@permissions.has_permission(['transaction.show'])
@filters.filters
def get_transaction(self, filter, id):
    transactions, status = service.get_transactions(id, filter)
    if status == 200:
        return APIResponse.success(transactions, "Transaction retrieved successfully")
    elif status == 404:
        return APIResponse.not_found("Transaction not found")
    return APIResponse.error("Failed to retrieve transaction", status_code=status)

@transactions.route('/', methods=['POST'])
#@cross_origin()
@permissions.has_permission(['transaction.add'])
@validate_json(TransactionCreateSchema)
def add_transaction(self, validated_data):
    message, status = service.create_transaction(validated_data)
    if status == 200 or status == 201:
        return APIResponse.created(message, "Transaction created successfully")
    return APIResponse.error(message, status_code=status)

@transactions.route('/<id>', methods=['PATCH'])
#@cross_origin()
@permissions.has_permission(['transaction.edit'])
@validate_json(TransactionUpdateSchema)
def update_transaction(self, validated_data, id):
    message, status = service.update_transaction(id, validated_data)
    if status == 200:
        return APIResponse.success(message, "Transaction updated successfully")
    elif status == 404:
        return APIResponse.not_found("Transaction not found")
    return APIResponse.error(message, status_code=status)


@transactions.route('/<id>', methods=['DELETE'])
#@cross_origin()
@permissions.has_permission(['transaction.delete'])
def delete_transaction(self, id):
    message, status = service.delete_transaction(id)
    if status == 200:
        return APIResponse.success(message, "Transaction deleted successfully")
    elif status == 404:
        return APIResponse.not_found("Transaction not found")
    return APIResponse.error(message, status_code=status)
