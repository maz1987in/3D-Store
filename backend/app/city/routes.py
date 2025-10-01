from flask_cors import CORS, cross_origin
from flask import Blueprint, request, jsonify, abort, make_response

from app.security import roles, permissions
from app.common import filters
from app.utilities.common_utils import is_valid_uuid

from .service import CityService

__uri__ = 'cities'
__blueprint__ = 'cities'

cities = Blueprint(__uri__, __name__)

service = CityService()

@cities.route('/', methods=['GET'])
#@cross_origin()
@filters.filters
def get_all_cities(filter):
    """Get all cities"""
    cities_data, status = service.get_cities(None, filter)
    return jsonify(cities_data), status

@cities.route('/active', methods=['GET'])
#@cross_origin()
def get_active_cities():
    """Get only active cities for public use"""
    cities_data, status = service.get_active_cities()
    return jsonify(cities_data), status

@cities.route('/<id>', methods=['GET'])
#@cross_origin()
@filters.filters
def get_city(filter, id):
    """Get a specific city by ID"""
    if not is_valid_uuid(id):
        abort(400, "Invalid city ID format")
    
    city_data, status = service.get_cities(id, filter)
    return jsonify(city_data), status

@cities.route('/', methods=['POST'])
#@cross_origin()
@permissions.has_permission(['city.add'])
@roles.token_required
def add_city(self):
    """Create a new city"""
    if not request.json:
        abort(400, "Invalid payload")
    
    required_fields = ['code', 'name']
    for field in required_fields:
        if field not in request.json:
            abort(400, f"Missing required field: {field}")
    
    message, status = service.create_city(request.json)
    return jsonify({'msg': message}), status

@cities.route('/<id>', methods=['PATCH'])
#@cross_origin()
@permissions.has_permission(['city.edit'])
@roles.token_required
def update_city(self, id):
    """Update an existing city"""
    if not is_valid_uuid(id):
        abort(400, "Invalid city ID format")
    
    if not request.json:
        abort(400, "Invalid payload")
    
    message, status = service.update_city(id, request.json)
    return jsonify({'msg': message}), status

@cities.route('/<id>', methods=['DELETE'])
#@cross_origin()
@permissions.has_permission(['city.delete'])
@roles.token_required
def delete_city(self, id):
    """Delete a city"""
    if not is_valid_uuid(id):
        abort(400, "Invalid city ID format")
    
    message, status = service.delete_city(id)
    return jsonify({'msg': message}), status