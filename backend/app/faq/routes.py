from flask_cors import CORS, cross_origin
from flask import Blueprint, request, jsonify, abort, make_response, g

from app.security import roles, permissions
from app.common import filters
from app.utils.response import APIResponse

from .service import FaqService

__uri__ = 'faqs'
__blueprint__ = 'faqs'

faqs = Blueprint(__uri__, __name__)

service = FaqService()

@faqs.route('/', methods=['GET'])
#@cross_origin()
@permissions.has_permission(['faq.show.all', 'faq.show'])
@filters.filters
def get_all_faqs(self, filter):
    faqs, status = service.get_faqs(None, filter)
    if status == 200:
        return APIResponse.success(faqs, "FAQs retrieved successfully")
    return APIResponse.error("Failed to retrieve FAQs", status_code=status)

@faqs.route('/<id>', methods=['GET'])
#@cross_origin()
@permissions.has_permission(['faq.show'])
@filters.filters
def get_faq(self, filter, id):
    faqs, status = service.get_faqs(id, filter)
    if status == 200:
        return APIResponse.success(faqs, "FAQ retrieved successfully")
    elif status == 404:
        return APIResponse.not_found("FAQ not found")
    return APIResponse.error("Failed to retrieve FAQ", status_code=status)


@faqs.route('/', methods=['POST'])
#@cross_origin()
@permissions.has_permission(['faq.add'])
def add_faq(self):
    message, status = service.create_faq(request.json)
    if status == 200 or status == 201:
        return APIResponse.created(message, "FAQ created successfully")
    return APIResponse.error(message, status_code=status)


@faqs.route('/<id>', methods=['PATCH'])
#@cross_origin()
@permissions.has_permission(['faq.edit'])
def update_faq(self, id):
    message, status = service.update_faq(id, request.json)
    if status == 200:
        return APIResponse.success(message, "FAQ updated successfully")
    elif status == 404:
        return APIResponse.not_found("FAQ not found")
    return APIResponse.error(message, status_code=status)


@faqs.route('/<id>', methods=['DELETE'])
#@cross_origin()
@permissions.has_permission(['faq.delete'])
def delete_faq(self, id):
    message, status = service.delete_faq(id)
    if status == 200:
        return APIResponse.success(message, "FAQ deleted successfully")
    elif status == 404:
        return APIResponse.not_found("FAQ not found")
    return APIResponse.error(message, status_code=status)


@faqs.route('/topic/<id>', methods=['GET'])
#@cross_origin()
@permissions.has_permission(['faq.show'])
def get_faq_by_key(self, id):
    faqs, status = service.get_faqs_by_faq_topic(id)
    if status == 200:
        return APIResponse.success({'faqs': faqs}, "FAQ topic retrieved successfully")
    elif status == 404:
        return APIResponse.not_found("FAQ topic not found")
    return APIResponse.error("Failed to retrieve FAQ topic", status_code=status)

@faqs.route('/topic/', methods=['GET'])
#@cross_origin()
@permissions.has_permission(['faq.show.all', 'faq.show'])
@filters.filters
def get_all_faq_topics(self, filter):
    faq_topic, status = service.get_faq_topics(None, filter)
    if status == 200:
        return APIResponse.success(faq_topic, "FAQ topics retrieved successfully")
    return APIResponse.error("Failed to retrieve FAQ topics", status_code=status)

@faqs.route('/topic/<id>', methods=['GET'])
#@cross_origin()
@permissions.has_permission(['faq.show'])
@filters.filters
def get_faq_topic(self, filter, id):
    faq_topic, status = service.get_faq_topics(id, filter)
    if status == 200:
        return APIResponse.success(faq_topic, "FAQ topic retrieved successfully")
    elif status == 404:
        return APIResponse.not_found("FAQ topic not found")
    return APIResponse.error("Failed to retrieve FAQ topic", status_code=status)


@faqs.route('/topic/', methods=['POST'])
#@cross_origin()
@permissions.has_permission(['faq.add'])
def add_faq_topic(self):
    message, status = service.create_faq_topic(request.json)
    if status == 200 or status == 201:
        return APIResponse.created(message, "FAQ topic created successfully")
    return APIResponse.error(message, status_code=status)


@faqs.route('/topic/<id>', methods=['PATCH'])
#@cross_origin()
@permissions.has_permission(['faq.edit'])
def update_faq_topic(self, id):
    message, status = service.update_faq_topic(id, request.json)
    if status == 200:
        return APIResponse.success(message, "FAQ topic updated successfully")
    elif status == 404:
        return APIResponse.not_found("FAQ topic not found")
    return APIResponse.error(message, status_code=status)


@faqs.route('/topic/<id>', methods=['DELETE'])
#@cross_origin()
@permissions.has_permission(['faq.delete'])
def delete_faq_topic(self, id):
    message, status = service.delete_faq_topic(id)
    if status == 200:
        return APIResponse.success(message, "FAQ topic deleted successfully")
    elif status == 404:
        return APIResponse.not_found("FAQ topic not found")
    return APIResponse.error(message, status_code=status)