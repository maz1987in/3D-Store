import json 
from flask_cors import CORS, cross_origin
from flask import Blueprint, request, jsonify, abort, make_response, g

from .service import FiscalYearService
from app.security import roles, permissions
from app.common import filters


__uri__ = 'fiscal_years'
__blueprint__ = 'fiscal_years'

fiscal_years = Blueprint(__uri__, __name__)

service = FiscalYearService()

@fiscal_years.route('/', methods=['GET'])
#@cross_origin()
#@permissions.has_permission(['fiscal_year.show'])
@roles.token_required
@filters.filters
def get_all_fiscal_years(filter,self):
    fiscal_years, status = service.get_fiscal_years(None,filter)
    return jsonify(fiscal_years), status

@fiscal_years.route('/<id>', methods=['GET'])
#@cross_origin()
#@permissions.has_permission(['fiscal_year.show'])
@roles.token_required
@filters.filters
def get_fiscal_year(filter,self, id):
    fiscal_years, status = service.get_fiscal_years(id, filter)
    return jsonify(fiscal_years), status

@fiscal_years.route('/', methods=['POST'])
#@cross_origin()
#@permissions.has_permission(['fiscal_year.add'])
@roles.token_required
def add_fiscal_year(self):
    if not request.json:
        abort(404)
    message, status = service.create_fiscal_year(request.json)
    return jsonify({'msg': message}), status

@fiscal_years.route('/<id>', methods=['PATCH'])
#@cross_origin()
#@permissions.has_permission(['fiscal_year.edit'])
@roles.token_required
def update_fiscal_year(self,id):
    if not request.json:
        abort(404)
    message, status = service.update_fiscal_year(id,request.json)
    return jsonify({'msg': message}), status

@fiscal_years.route('/<id>', methods=['DELETE'])
#@cross_origin()
#@permissions.has_permission(['fiscal_year.delete'])
@roles.token_required
def delete_fiscal_year(self, id):
    message, status = service.delete_fiscal_year(id)
    return jsonify({'msg': message}), status

@fiscal_years.route('/open', methods=['GET'])
@roles.token_required
@filters.filters
def get_open_fiscal_years(filter, self):
    fiscal_years, status = service.get_open_fiscal_years(filter)
    return jsonify(fiscal_years), status

@fiscal_years.route('/current-open-unlocked', methods=['GET'])
@roles.token_required
def get_current_open_unlocked_fiscal_year():
    fiscal_year, status = service.get_current_open_unlocked_fiscal_year()
    return jsonify(fiscal_year), status

@fiscal_years.route('/periods', methods=['GET'])
@roles.token_required
@filters.filters
def get_all_fiscal_periods(filter, self):
    fiscal_periods, status = service.get_fiscal_periods(None, filter)
    return jsonify(fiscal_periods), status

@fiscal_years.route('/periods/<id>', methods=['GET'])
@roles.token_required
@filters.filters
def get_fiscal_period(filter, self, id):
    fiscal_periods, status = service.get_fiscal_periods(id, filter)
    return jsonify(fiscal_periods), status

@fiscal_years.route('/periods', methods=['POST'])
@roles.token_required
def add_fiscal_period(self):
    if not request.json:
        abort(404)
    message, status = service.create_fiscal_period(request.json)
    return jsonify({'msg': message}), status

@fiscal_years.route('/periods/<id>', methods=['PATCH'])
@roles.token_required
def update_fiscal_period(self, id):
    if not request.json:
        abort(404)
    message, status = service.update_fiscal_period(id, request.json)
    return jsonify({'msg': message}), status

@fiscal_years.route('/periods/<id>', methods=['DELETE'])
@roles.token_required
def delete_fiscal_period(self, id):
    message, status = service.delete_fiscal_period(id)
    return jsonify({'msg': message}), status