from flask_cors import CORS, cross_origin
from flask import Blueprint, request, jsonify, abort, make_response, g

from app.security import roles, permissions
from app.common import filters

from .service import FaqService

__uri__ = 'faqs'
__blueprint__ = 'faqs'

faqs = Blueprint(__uri__, __name__)

service = FaqService()

@faqs.route('/', methods=['GET'])
#@cross_origin()
#@permissions.has_permission(['faq.show.all', 'faq.show'])
@filters.filters
def get_all_faqs(filter):
    faqs , status = service.get_faqs(None, filter)
    return jsonify(faqs), status

@faqs.route('/<id>', methods=['GET'])
#@cross_origin()
#@permissions.has_permission(['faq.show'])
@filters.filters
def get_faq(filter,id):
    faqs, status = service.get_faqs(id, filter)
    return jsonify(faqs), status


@faqs.route('/', methods=['POST'])
#@cross_origin()
@permissions.has_permission(['faq.add'])
def add_faq(self):
    #if not request.json or not 'key' in request.json:
    #    abort(404)    
    message, status = service.create_faq(request.json)
    return jsonify({'msg': message}), status


@faqs.route('/<id>', methods=['PATCH'])
#@cross_origin()
@permissions.has_permission(['faq.edit'])
def update_faq(self,id):
    message, status = service.update_faq(id, request.json)
    return jsonify({'msg': message}), status


@faqs.route('/<id>', methods=['DELETE'])
#@cross_origin()
@permissions.has_permission(['faq.delete'])
def delete_faq(self,id):
    message, status = service.delete_faq(id)
    return jsonify({'msg': message}), status


@faqs.route('/topic/<id>', methods=['GET'])
#@cross_origin()
#@permissions.has_permission(['faq.show'])
def get_faq_by_key(id):
    faqs, status = service.get_faqs_by_faq_topic(id)
    return jsonify({'faqs': faqs}),status

@faqs.route('/topic/', methods=['GET'])
#@cross_origin()
#@permissions.has_permission(['faq.show.all', 'faq.show'])
@filters.filters
def get_all_faq_topics(filter):
    faq_topic, status = service.get_faq_topics(None, filter)
    return jsonify(faq_topic), status

@faqs.route('/topic/<id>', methods=['GET'])
#@cross_origin()
#@permissions.has_permission(['faq.show'])
@filters.filters
def get_faq_topic(filter,id):
    faq_topic, status = service.get_faq_topics(id, filter)
    return jsonify(faq_topic), status


@faqs.route('/topic/', methods=['POST'])
#@cross_origin()
@permissions.has_permission(['faq.add'])
def add_faq_topic(self):
    #if not request.json or not 'key' in request.json:
    #    abort(404)    
    message, status = service.create_faq_topic(request.json)
    return jsonify({'msg': message}), status


@faqs.route('/topic/<id>', methods=['PATCH'])
#@cross_origin()
@permissions.has_permission(['faq.edit'])
def update_faq_topic(self,id):
    message, status = service.update_faq_topic(id, request.json)
    return jsonify({'msg': message}), status


@faqs.route('/topic/<id>', methods=['DELETE'])
#@cross_origin()
@permissions.has_permission(['faq.delete'])
def delete_faq_topic(self,id):
    message, status = service.delete_faq_topic(id)
    return jsonify({'msg': message}), status