import json 
from flask_cors import CORS, cross_origin
from flask import Blueprint, request, jsonify, abort, make_response, g
from app.common.enum import PlatformEnum

from app.security import roles, permissions
from app.common import filters

from .service import LaborService

__uri__ = 'labors'
__blueprint__ = 'labors'

labors = Blueprint(__uri__, __name__)

labor_service = LaborService()

@labors.route('/', methods=['GET'])
#@cross_origin()
#@permissions.has_permission(['labor.show'])
@roles.token_required
@filters.filters
def get_all_labors(filter,self):
    labors, status = labor_service.get_labors(None,filter)
    return jsonify(labors), status

@labors.route('/f/', methods=['GET'])
@roles.token_required
@filters.filters
def get_labors_f(filter, self):
    labors, status = labor_service.get_labors_f(filter)
    return jsonify(labors), status

@labors.route('/<id>', methods=['GET'])
#@cross_origin()
#@permissions.has_permission(['labor.show'])
@roles.token_required
@filters.filters
def get_labor(filter,self, id):
    labors, status = labor_service.get_labors(id, filter)
    return jsonify(labors), status

@labors.route('/', methods=['POST'])
#@cross_origin()
#@permissions.has_permission(['labor.add'])
@roles.token_required
def add_labor(self):
    if not request.json:
        abort(404)
    message, status = labor_service.create_labor(request.json)
    return jsonify({'msg': message}), status

@labors.route('/<id>', methods=['PATCH'])
#@cross_origin()
#@permissions.has_permission(['labor.edit'])
@roles.token_required
def update_labor(self,id):
    if not request.json:
        abort(404)
    message, status = labor_service.update_labor(id,request.json)
    return jsonify({'msg': message}), status


@labors.route('/<id>', methods=['DELETE'])
#@cross_origin()
#@permissions.has_permission(['labor.delete'])
@roles.token_required
def delete_labor(self, id):
    message, status = labor_service.delete_labor(id)
    return jsonify({'msg': message}), status

@labors.route('/category/', methods=['GET'])
#@cross_origin()
#@permissions.has_permission(['labor_category.show'])
@roles.token_required
@filters.filters
def get_all_labor_categories(filter,self):
    categories, status = labor_service.get_labor_categories(None,filter)
    return jsonify(categories), status

@labors.route('/category/<id>', methods=['GET'])
#@cross_origin()
#@permissions.has_permission(['labor_category.show'])
@roles.token_required
@filters.filters
def get_labor_category(filter,self, id):
    categories, status = labor_service.get_labor_categories(id, filter)
    return jsonify(categories), status

@labors.route('/category/', methods=['POST'])
#@cross_origin()
#@permissions.has_permission(['labor_category.add'])
@roles.token_required
def add_labor_category(self):
    if not request.json:
        abort(404)
    message, status = labor_service.create_labor_category(request.json)
    return jsonify({'msg': message}), status

@labors.route('/category/<id>', methods=['PATCH'])
#@cross_origin()
#@permissions.has_permission(['labor_category.edit'])
@roles.token_required
def update_labor_category(self,id):
    if not request.json:
        abort(404)
    message, status = labor_service.update_labor_category(id,request.json)
    return jsonify({'msg': message}), status


@labors.route('/category/<id>', methods=['DELETE'])
#@cross_origin()
#@permissions.has_permission(['labor_category.delete'])
@roles.token_required
def delete_labor_category(self, id):
    message, status = labor_service.delete_labor_category(id)
    return jsonify({'msg': message}), status