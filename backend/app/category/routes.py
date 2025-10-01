from flask_cors import CORS, cross_origin
from flask import Blueprint, request, jsonify, abort, make_response

from app.security import roles , permissions
from app.common import filters
from app.utilities.common_utils import is_valid_uuid
from app.decorators.validation import validate_json, validate_form_data
from app.utils.response import APIResponse
from .schemas import CategoryCreateSchema, CategoryUpdateSchema

from .service import CategoryService

__uri__ = 'categories'
__blueprint__ = 'categories'

categories = Blueprint(__uri__, __name__)

service = CategoryService()

@categories.route('/', methods=['GET'])
@cross_origin()
@permissions.has_permission(['category.show.all'])
@filters.filters
def get_all_categories():
    categories = service.get_categories_all()
    return APIResponse.success(categories, "Categories retrieved successfully")

@categories.route('/<id>', methods=['GET'])
@cross_origin()
@permissions.has_permission(['category.show.all'])
@filters.filters
def get_category(filter, id):
    if is_valid_uuid(id):
        category = service.get_categories(id, filter)
        return APIResponse.success(category, "Category retrieved successfully")
    else:
        return APIResponse.not_found("Invalid category ID format")

@categories.route('/dependencies/<parent_id>', methods=['GET'])
@cross_origin()
@roles.token_required
def get_categories_dependency(self, parent_id):
    if is_valid_uuid(parent_id):
        categories = service.get_categories_dependency(parent_id)
        return APIResponse.success(categories, "Category dependencies retrieved successfully")
    else:
        return APIResponse.not_found("Invalid parent category ID format")


@categories.route('/', methods=['POST'])
@cross_origin()
@permissions.has_permission(['category.add'])
@roles.token_required
@validate_form_data(CategoryCreateSchema)
def add_category(self, validated_data):
    message, status = service.create_category(validated_data, request.files['icon'] if 'icon' in request.files else None)
    if status == 200:
        return APIResponse.success(message=message)
    else:
        return APIResponse.error(message, status_code=status)

@categories.route('/<id>', methods=['PATCH'])
@cross_origin()
@permissions.has_permission(['category.edit'])
@roles.token_required
@validate_form_data(CategoryUpdateSchema)
def update_category(self, validated_data, id):
    if not is_valid_uuid(id):
        return APIResponse.not_found("Invalid category ID format")
    message, status = service.update_category(id, validated_data, request.files['icon'] if 'icon' in request.files else None)
    if status == 200:
        return APIResponse.success(message=message)
    else:
        return APIResponse.error(message, status_code=status)

@categories.route('/<id>', methods=['DELETE'])
@cross_origin()
@permissions.has_permission(['category.delete'])
@roles.token_required
def delete_category(self, id):
    if not is_valid_uuid(id):
        return APIResponse.not_found("Invalid category ID format")
    message, status = service.delete_category(id)
    if status == 200:
        return APIResponse.success(message=message)
    else:
        return APIResponse.error(message, status_code=status)
