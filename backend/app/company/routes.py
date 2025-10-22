import json 
from flask_cors import CORS, cross_origin
from flask import Blueprint, request, jsonify, abort, make_response, g
from app.common.enum import PlatformEnum

from app.security import roles, permissions
from app.common import filters
from app.utils.response import APIResponse
from app.decorators.validation import validate_json
from .schemas import CompanyCreateSchema, CompanyUpdateSchema

from .service import CompanyService

__uri__ = 'companies'
__blueprint__ = 'companies'

companies = Blueprint(__uri__, __name__)

service = CompanyService()

@companies.route('/', methods=['GET'])
#@cross_origin()
@permissions.has_permission(['company.show'])
@filters.filters
def get_all_companies(self, filter):
    companies, status = service.get_companies(None, filter)
    if status == 200:
        return APIResponse.success(companies, "Companies retrieved successfully")
    return APIResponse.error("Failed to retrieve companies", status_code=status)

@companies.route('/<id>', methods=['GET'])
#@cross_origin()
@permissions.has_permission(['company.show'])
@filters.filters
def get_company(self, filter, id):
    companies, status = service.get_companies(id, filter)
    if status == 200:
        return APIResponse.success(companies, "Company retrieved successfully")
    elif status == 404:
        return APIResponse.not_found("Company not found")
    return APIResponse.error("Failed to retrieve company", status_code=status)

@companies.route('/', methods=['POST'])
#@cross_origin()
@permissions.has_permission(['company.add'])
@validate_json(CompanyCreateSchema)
def add_company(self, validated_data):
    message, status = service.create_company(validated_data)
    if status == 200 or status == 201:
        return APIResponse.created(message, "Company created successfully")
    return APIResponse.error(message, status_code=status)

@companies.route('/<id>', methods=['PATCH'])
#@cross_origin()
@permissions.has_permission(['company.edit'])
@validate_json(CompanyUpdateSchema)
def update_company(self, validated_data, id):
    message, status = service.update_company(id, validated_data)
    if status == 200:
        return APIResponse.success(message, "Company updated successfully")
    elif status == 404:
        return APIResponse.not_found("Company not found")
    return APIResponse.error(message, status_code=status)


@companies.route('/<id>', methods=['DELETE'])
#@cross_origin()
@permissions.has_permission(['company.delete'])
def delete_company(self, id):
    message, status = service.delete_company(id)
    if status == 200:
        return APIResponse.success(message, "Company deleted successfully")
    elif status == 404:
        return APIResponse.not_found("Company not found")
    return APIResponse.error(message, status_code=status)