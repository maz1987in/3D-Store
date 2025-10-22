import json 
from flask_cors import CORS, cross_origin
from flask import Blueprint, request, jsonify, abort, make_response, g

from .service import FiscalYearService
from app.security import roles, permissions
from app.common import filters
from app.utils.response import APIResponse
from app.decorators.validation import validate_json
from .schemas import FiscalYearCreateSchema, FiscalYearUpdateSchema, FiscalPeriodCreateSchema, FiscalPeriodUpdateSchema


__uri__ = 'fiscal_years'
__blueprint__ = 'fiscal_years'

fiscal_years = Blueprint(__uri__, __name__)

service = FiscalYearService()

@fiscal_years.route('/', methods=['GET'])
#@cross_origin()
@permissions.has_permission(['fiscal_year.show'])
@filters.filters
def get_all_fiscal_years(self, filter):
    fiscal_years, status = service.get_fiscal_years(None, filter)
    if status == 200:
        return APIResponse.success(fiscal_years, "Fiscal years retrieved successfully")
    return APIResponse.error("Failed to retrieve fiscal years", status_code=status)

@fiscal_years.route('/<id>', methods=['GET'])
#@cross_origin()
@permissions.has_permission(['fiscal_year.show'])
@filters.filters
def get_fiscal_year(self, filter, id):
    fiscal_years, status = service.get_fiscal_years(id, filter)
    if status == 200:
        return APIResponse.success(fiscal_years, "Fiscal year retrieved successfully")
    elif status == 404:
        return APIResponse.not_found("Fiscal year not found")
    return APIResponse.error("Failed to retrieve fiscal year", status_code=status)

@fiscal_years.route('/', methods=['POST'])
#@cross_origin()
@permissions.has_permission(['fiscal_year.add'])
@validate_json(FiscalYearCreateSchema)
def add_fiscal_year(self, validated_data):
    message, status = service.create_fiscal_year(validated_data)
    if status == 200 or status == 201:
        return APIResponse.created(message, "Fiscal year created successfully")
    return APIResponse.error(message, status_code=status)

@fiscal_years.route('/<id>', methods=['PATCH'])
#@cross_origin()
@permissions.has_permission(['fiscal_year.edit'])
@validate_json(FiscalYearUpdateSchema)
def update_fiscal_year(self, validated_data, id):
    message, status = service.update_fiscal_year(id, validated_data)
    if status == 200:
        return APIResponse.success(message, "Fiscal year updated successfully")
    elif status == 404:
        return APIResponse.not_found("Fiscal year not found")
    return APIResponse.error(message, status_code=status)

@fiscal_years.route('/<id>', methods=['DELETE'])
#@cross_origin()
@permissions.has_permission(['fiscal_year.delete'])
def delete_fiscal_year(self, id):
    message, status = service.delete_fiscal_year(id)
    if status == 200:
        return APIResponse.success(message, "Fiscal year deleted successfully")
    elif status == 404:
        return APIResponse.not_found("Fiscal year not found")
    return APIResponse.error(message, status_code=status)

@fiscal_years.route('/open', methods=['GET'])
@roles.token_required
@filters.filters
def get_open_fiscal_years(self, filter):
    fiscal_years, status = service.get_open_fiscal_years(filter)
    if status == 200:
        return APIResponse.success(fiscal_years, "Open fiscal years retrieved successfully")
    return APIResponse.error("Failed to retrieve open fiscal years", status_code=status)

@fiscal_years.route('/current-open-unlocked', methods=['GET'])
@roles.token_required
def get_current_open_unlocked_fiscal_year():
    fiscal_year, status = service.get_current_open_unlocked_fiscal_year()
    if status == 200:
        return APIResponse.success(fiscal_year, "Current fiscal year retrieved successfully")
    elif status == 404:
        return APIResponse.not_found("No open unlocked fiscal year found")
    return APIResponse.error("Failed to retrieve current fiscal year", status_code=status)

@fiscal_years.route('/periods', methods=['GET'])
@roles.token_required
@filters.filters
def get_all_fiscal_periods(self, filter):
    fiscal_periods, status = service.get_fiscal_periods(None, filter)
    if status == 200:
        return APIResponse.success(fiscal_periods, "Fiscal periods retrieved successfully")
    return APIResponse.error("Failed to retrieve fiscal periods", status_code=status)

@fiscal_years.route('/periods/<id>', methods=['GET'])
@roles.token_required
@filters.filters
def get_fiscal_period(self, filter, id):
    fiscal_periods, status = service.get_fiscal_periods(id, filter)
    if status == 200:
        return APIResponse.success(fiscal_periods, "Fiscal period retrieved successfully")
    elif status == 404:
        return APIResponse.not_found("Fiscal period not found")
    return APIResponse.error("Failed to retrieve fiscal period", status_code=status)

@fiscal_years.route('/periods', methods=['POST'])
@roles.token_required
@validate_json(FiscalPeriodCreateSchema)
def add_fiscal_period(self, validated_data):
    message, status = service.create_fiscal_period(validated_data)
    if status == 200 or status == 201:
        return APIResponse.created(message, "Fiscal period created successfully")
    return APIResponse.error(message, status_code=status)

@fiscal_years.route('/periods/<id>', methods=['PATCH'])
@roles.token_required
@validate_json(FiscalPeriodUpdateSchema)
def update_fiscal_period(self, validated_data, id):
    message, status = service.update_fiscal_period(id, validated_data)
    if status == 200:
        return APIResponse.success(message, "Fiscal period updated successfully")
    elif status == 404:
        return APIResponse.not_found("Fiscal period not found")
    return APIResponse.error(message, status_code=status)

@fiscal_years.route('/periods/<id>', methods=['DELETE'])
@roles.token_required
def delete_fiscal_period(self, id):
    message, status = service.delete_fiscal_period(id)
    if status == 200:
        return APIResponse.success(message, "Fiscal period deleted successfully")
    elif status == 404:
        return APIResponse.not_found("Fiscal period not found")
    return APIResponse.error(message, status_code=status)
