from flask_cors import CORS, cross_origin
from flask import Blueprint, request, jsonify, abort, make_response, g

from app.security import roles, permissions
from app.common import filters
from app.utilities.common_utils import get_owner_id

from .service import TemplatesContentService

__uri__ = 'templates_contents'
__blueprint__ = 'templates_contents'

templates_contents = Blueprint(__uri__, __name__)

service = TemplatesContentService()

@templates_contents.route('/', methods=['GET'])
#@cross_origin()
@permissions.has_permission(['templates_content.show.all', 'templates_content.show'])
@filters.filters
def get_all_templates_contents(filter, self):
    templates_contents, status = service.get_templates_contents(None, filter)
    return jsonify(templates_contents), status

@templates_contents.route('/<id>', methods=['GET'])
#@cross_origin()
@permissions.has_permission(['templates_content.show.all','templates_content.show'])
@filters.filters
def get_templates_content(filter,self,id):
    templates_contents, status = service.get_templates_contents(id, filter)
    return jsonify(templates_contents), status


@templates_contents.route('/', methods=['POST'])
#@cross_origin()
@permissions.has_permission(['templates_content.add'])
def add_templates_content(self):
    if not request.json or 'key' not in request.json:
        abort(404)    
    message, status = service.create_templates_content(request.json)
    return jsonify({'msg': message}), status


@templates_contents.route('/<id>', methods=['PATCH'])
#@cross_origin()
@permissions.has_permission(['templates_content.edit'])
def update_templates_content(self,id):
    message, status = service.update_templates_content(id, request.json)
    return jsonify({'msg': message}), status


@templates_contents.route('/<id>', methods=['DELETE'])
#@cross_origin()
@permissions.has_permission(['templates_content.delete'])
def delete_templates_content(self,id):
    message, status = service.delete_templates_content(id)
    return jsonify({'msg': message}), status


@templates_contents.route('/key/<key>', methods=['GET'])
#@cross_origin()
@permissions.has_permission(['templates_content.show.all','templates_content.show'])
def get_templates_content_by_key(self,key):
    templates_contents, status = service.get_templates_contents_by_key(key)
    return jsonify({'templates_contents': templates_contents}), status

@templates_contents.route('/key/<key>/id/<id>', methods=['DELETE'])
#@cross_origin()
@permissions.has_permission(['templates_content.delete'])
def delete_templates_content_by_key(self,key, id):
    message, status = service.delete_templates_contents_by_key_and_model_id(key)
    return jsonify({'msg': message}), status

@templates_contents.route('/model/<model_type>', defaults={'model_op': None}, methods=['GET'])
@templates_contents.route('/model/<model_type>/<model_op>', methods=['GET'])
#@cross_origin()
@permissions.has_permission(['templates_content.show.all','templates_content.show'])
def get_templates_contents_by_model_and_op(self,model_type=None, model_op=None):
    templates_contents, status = service.get_templates_contents_by_model_and_op(model_type,model_op)
    return jsonify({'templates_contents': templates_contents}), status


@templates_contents.route('/media_type', methods=['GET'])
@permissions.has_permission(['templates_content.show.all','templates_content.show'])
def get_templates_contents_by_media_type(self):
    media_type, status = service.get_media_types_enum()
    return jsonify({'media_type': list(media_type)}), status