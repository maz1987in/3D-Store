import json 
from flask_cors import CORS, cross_origin
from flask import Blueprint, request, jsonify, abort, make_response, g
from app.common.enum import PlatformEnum

from app.security import roles, permissions
from app.common import filters
from app.utils.response import APIResponse
from app.decorators.validation import validate_json
from .schemas import ExpenseCreateSchema, ExpenseUpdateSchema

from .service import ExpenseService

__uri__ = 'expenses'
__blueprint__ = 'expenses'

expenses = Blueprint(__uri__, __name__)

expense_service = ExpenseService()

@expenses.route('/', methods=['GET'])
#@cross_origin()
@permissions.has_permission(['expense.show'])
@filters.filters
def get_all_expenses(self, filter):
    expenses, status = expense_service.get_expenses(None, filter)
    if status == 200:
        return APIResponse.success(expenses, "Expenses retrieved successfully")
    return APIResponse.error("Failed to retrieve expenses", status_code=status)

@expenses.route('/<id>', methods=['GET'])
#@cross_origin()
@permissions.has_permission(['expense.show'])
@filters.filters
def get_expense(self, filter, id):
    expenses, status = expense_service.get_expenses(id, filter)
    if status == 200:
        return APIResponse.success(expenses, "Expense retrieved successfully")
    elif status == 404:
        return APIResponse.not_found("Expense not found")
    return APIResponse.error("Failed to retrieve expense", status_code=status)

@expenses.route('/', methods=['POST'])
#@cross_origin()
@permissions.has_permission(['expense.add'])
def add_expense(self):
    if request.is_json:
        param = request.json
    else:
        dictionary = request.form.to_dict(flat=False)
        list = dictionary['form']
        param = json.loads(list[0])

    if not param:
        return APIResponse.validation_error("No expense data provided")
    
    message, status = expense_service.create_expense(param, request.files)
    if status == 200 or status == 201:
        return APIResponse.created(message, "Expense created successfully")
    return APIResponse.error(message, status_code=status)

@expenses.route('/<id>', methods=['PATCH'])
#@cross_origin()
@permissions.has_permission(['expense.edit'])
def update_expense(self, id):
    if request.is_json:
        param = request.json
    else:
        dictionary = request.form.to_dict(flat=False)
        list = dictionary['form']
        param = json.loads(list[0])

    message, status = expense_service.update_expense(id, param, request.files)
    if status == 200:
        return APIResponse.success(message, "Expense updated successfully")
    elif status == 404:
        return APIResponse.not_found("Expense not found")
    return APIResponse.error(message, status_code=status)

@expenses.route('/<id>', methods=['DELETE'])
#@cross_origin()
@permissions.has_permission(['expense.delete'])
def delete_expense(self, id):
    message, status = expense_service.delete_expense(id)
    if status == 200:
        return APIResponse.success(message, "Expense deleted successfully")
    elif status == 404:
        return APIResponse.not_found("Expense not found")
    return APIResponse.error(message, status_code=status)

@expenses.route('/<id>/reindex', methods=['GET'])
@permissions.has_permission(['expense.show'])
def reindex_expense(self, id):
    response, status = expense_service.reindex_expense_attachments(id)
    if status == 200:
        return APIResponse.success(response, "Expense attachments reindexed successfully")
    return APIResponse.error("Failed to reindex expense attachments", status_code=status)

@expenses.route('/upload/<id>/<int:order>', defaults={'new': None}, methods=['POST'])
@expenses.route('/upload/<id>/<int:order>/<new>', methods=['POST'])
@permissions.has_permission(['expense.add'])
def expense_upload_file(self, id, order, new=None):
    if not request.files:
        return APIResponse.validation_error("No files provided in the request")
    
    is_new = new is not None
    message, files, status = expense_service.upload_expense_files(id, request.files.getlist('file'), order, is_new)
    
    if status == 200:
        return APIResponse.success({'msg': message, 'files': files}, "Files uploaded successfully")
    return APIResponse.error(message, status_code=status)

@expenses.route('/upload/<id>', methods=['DELETE'])
@permissions.has_permission(['expense.delete'])
def expense_delete_upload_file(self, id):
    message, status = expense_service.delete_expense_file(id)
    if status == 200:
        return APIResponse.success(message, "File deleted successfully")
    elif status == 404:
        return APIResponse.not_found("File not found")
    return APIResponse.error(message, status_code=status)

@expenses.route('/category/', methods=['GET'])
#@cross_origin()
@permissions.has_permission(['expense_category.show'])
@filters.filters
def get_all_expense_categories(self, filter):
    categories, status = expense_service.get_expense_categories(None, filter)
    if status == 200:
        return APIResponse.success(categories, "Expense categories retrieved successfully")
    return APIResponse.error("Failed to retrieve expense categories", status_code=status)

@expenses.route('/category/<id>', methods=['GET'])
#@cross_origin()
@permissions.has_permission(['expense_category.show'])
@filters.filters
def get_expense_category(self, filter, id):
    categories, status = expense_service.get_expense_categories(id, filter)
    if status == 200:
        return APIResponse.success(categories, "Expense category retrieved successfully")
    elif status == 404:
        return APIResponse.not_found("Expense category not found")
    return APIResponse.error("Failed to retrieve expense category", status_code=status)

@expenses.route('/category/', methods=['POST'])
#@cross_origin()
@permissions.has_permission(['expense_category.add'])
def add_expense_category(self):
    if not request.json:
        return APIResponse.validation_error("No data provided")
    
    message, status = expense_service.create_expense_category(request.json)
    if status == 200 or status == 201:
        return APIResponse.created(message, "Expense category created successfully")
    return APIResponse.error(message, status_code=status)

@expenses.route('/category/<id>', methods=['PATCH'])
#@cross_origin()
@permissions.has_permission(['expense_category.edit'])
def update_expense_category(self, id):
    if not request.json:
        return APIResponse.validation_error("No data provided")
    
    message, status = expense_service.update_expense_category(id, request.json)
    if status == 200:
        return APIResponse.success(message, "Expense category updated successfully")
    elif status == 404:
        return APIResponse.not_found("Expense category not found")
    return APIResponse.error(message, status_code=status)

@expenses.route('/category/<id>', methods=['DELETE'])
#@cross_origin()
@permissions.has_permission(['expense_category.delete'])
def delete_expense_category(self, id):
    message, status = expense_service.delete_expense_category(id)
    if status == 200:
        return APIResponse.success(message, "Expense category deleted successfully")
    elif status == 404:
        return APIResponse.not_found("Expense category not found")
    return APIResponse.error(message, status_code=status)
