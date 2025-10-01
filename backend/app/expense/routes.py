import json 
from flask_cors import CORS, cross_origin
from flask import Blueprint, request, jsonify, abort, make_response, g
from app.common.enum import PlatformEnum

from app.security import roles, permissions
from app.common import filters

from .service import ExpenseService

__uri__ = 'expenses'
__blueprint__ = 'expenses'

expenses = Blueprint(__uri__, __name__)

expense_service = ExpenseService()

@expenses.route('/', methods=['GET'])
#@cross_origin()
#@permissions.has_permission(['expense.show'])
@roles.token_required
@filters.filters
def get_all_expenses(filter, self):
    expenses, status = expense_service.get_expenses(None, filter)
    return jsonify(expenses), status

@expenses.route('/<id>', methods=['GET'])
#@cross_origin()
#@permissions.has_permission(['expense.show'])
@roles.token_required
@filters.filters
def get_expense(filter, self, id):
    expenses, status = expense_service.get_expenses(id, filter)
    return jsonify(expenses), status

@expenses.route('/', methods=['POST'])
#@cross_origin()
#@permissions.has_permission(['expense.add'])
@roles.token_required
def add_expense(self):
    if request.is_json:
        param = request.json
    else:
        dictionary = request.form.to_dict(flat=False)
        list = dictionary['form']
        param = json.loads(list[0])

    if not param:
        abort(404)
    message, status = expense_service.create_expense(param, request.files)
    return jsonify({'msg': message}), status

@expenses.route('/<id>', methods=['PATCH'])
#@cross_origin()
#@permissions.has_permission(['expense.edit'])
@roles.token_required
def update_expense(self, id):
    if request.is_json:
        param = request.json
    else:
        dictionary = request.form.to_dict(flat=False)
        list = dictionary['form']
        param = json.loads(list[0])

    message, status = expense_service.update_expense(id, param, request.files)
    return jsonify({'msg': message}), status

@expenses.route('/<id>', methods=['DELETE'])
#@cross_origin()
#@permissions.has_permission(['expense.delete'])
@roles.token_required
def delete_expense(self, id):
    message, status = expense_service.delete_expense(id)
    return jsonify({'msg': message}), status

@expenses.route('/<id>/reindex', methods=['GET'])
#@permissions.has_permission(['expense.show'])
@roles.token_required
def reindex_expense(self, id):
    response, status = expense_service.reindex_expense_attachments(id)
    return jsonify(response), status

@expenses.route('/upload/<id>/<int:order>', defaults={'new': None}, methods=['POST'])
@expenses.route('/upload/<id>/<int:order>/<new>', methods=['POST'])
#@permissions.has_permission(['expense.add'])
@roles.token_required
def expense_upload_file(self, id, order, new=None):
    if not request.files:
        abort(404)
    is_new = new is not None

    message, files, status = expense_service.upload_expense_files(id, request.files.getlist('file'), order, is_new)
    return jsonify({'msg': message, 'files': files}), status

@expenses.route('/upload/<id>', methods=['DELETE'])
#@permissions.has_permission(['expense.delete'])
@roles.token_required
def expense_delete_upload_file(self, id):
    message, status = expense_service.delete_expense_file(id)
    return jsonify({'msg': message}), status

@expenses.route('/category/', methods=['GET'])
#@cross_origin()
#@permissions.has_permission(['expense_category.show'])
@roles.token_required
@filters.filters
def get_all_expense_categories(filter, self):
    categories, status = expense_service.get_expense_categories(None, filter)
    return jsonify(categories), status

@expenses.route('/category/<id>', methods=['GET'])
#@cross_origin()
#@permissions.has_permission(['expense_category.show'])
@roles.token_required
@filters.filters
def get_expense_category(filter, self, id):
    categories, status = expense_service.get_expense_categories(id, filter)
    return jsonify(categories), status

@expenses.route('/category/', methods=['POST'])
#@cross_origin()
#@permissions.has_permission(['expense_category.add'])
@roles.token_required
def add_expense_category(self):
    if not request.json:
        abort(404)
    message, status = expense_service.create_expense_category(request.json)
    return jsonify({'msg': message}), status

@expenses.route('/category/<id>', methods=['PATCH'])
#@cross_origin()
#@permissions.has_permission(['expense_category.edit'])
@roles.token_required
def update_expense_category(self, id):
    if not request.json:
        abort(404)
    message, status = expense_service.update_expense_category(id, request.json)
    return jsonify({'msg': message}), status

@expenses.route('/category/<id>', methods=['DELETE'])
#@cross_origin()
#@permissions.has_permission(['expense_category.delete'])
@roles.token_required
def delete_expense_category(self, id):
    message, status = expense_service.delete_expense_category(id)
    return jsonify({'msg': message}), status