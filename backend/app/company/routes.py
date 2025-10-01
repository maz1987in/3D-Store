import json 
from flask_cors import CORS, cross_origin
from flask import Blueprint, request, jsonify, abort, make_response, g
from app.common.enum import PlatformEnum

from app.security import roles, permissions
from app.common import filters

from .service import CompanyService

__uri__ = 'companies'
__blueprint__ = 'companies'

companies = Blueprint(__uri__, __name__)

service = CompanyService()

@companies.route('/', methods=['GET'])
#@cross_origin()
#@permissions.has_permission(['company.show'])
@roles.token_required
@filters.filters
def get_all_companies(filter,self):
    companies, status = service.get_companies(None,filter)
    return jsonify(companies), status

@companies.route('/<id>', methods=['GET'])
#@cross_origin()
#@permissions.has_permission(['company.show'])
@roles.token_required
@filters.filters
def get_company(filter,self, id):
    companies, status = service.get_companies(id, filter)
    return jsonify(companies), status

@companies.route('/', methods=['POST'])
#@cross_origin()
#@permissions.has_permission(['company.add'])
@roles.token_required
def add_company(self):
    if not request.json:
        abort(404)
    message, status = service.create_company(request.json)
    return jsonify({'msg': message}), status

@companies.route('/<id>', methods=['PATCH'])
#@cross_origin()
#@permissions.has_permission(['company.edit'])
@roles.token_required
def update_company(self,id):
    if not request.json:
        abort(404)
    message, status = service.update_company(id,request.json)
    return jsonify({'msg': message}), status


@companies.route('/<id>', methods=['DELETE'])
#@cross_origin()
#@permissions.has_permission(['company.delete'])
@roles.token_required
def delete_company(self, id):
    message, status = service.delete_company(id)
    return jsonify({'msg': message}), status