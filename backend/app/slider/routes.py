import json 
from flask_cors import CORS, cross_origin
from flask import Blueprint, request, jsonify, abort, make_response, g
from app.common.enum import PlatformEnum

from app.security import roles, permissions
from app.common import filters

from .service import SliderService

__uri__ = 'sliders'
__blueprint__ = 'sliders'

sliders = Blueprint(__uri__, __name__)

service = SliderService()

@sliders.route('/', methods=['GET'])
#@cross_origin()
@permissions.has_permission(['slider.show'])
@filters.filters
def get_all_sliders(filter,self):
    sliders, status = service.get_sliders(None,filter)
    return jsonify(sliders), status

@sliders.route('/<id>', methods=['GET'])
#@cross_origin()
@permissions.has_permission(['slider.show'])
@filters.filters
def get_slider(filter,self, id):
    sliders, status = service.get_sliders(id, filter)
    return jsonify(sliders), status

@sliders.route('/today/<platform>', methods=['GET'])
#@cross_origin()
def get_sliders_today(platform=PlatformEnum.ALL):
    sliders, status = service.get_slider_today(platform)
    return jsonify(sliders), status


@sliders.route('/', methods=['POST'])
#@cross_origin()
@permissions.has_permission(['slider.add'])
def add_slider(self):
    if request.is_json:
        param = request.json
    else:
        dictionary = request.form.to_dict(flat=False)
        list_data = dictionary['form'] if 'form' in dictionary else request.form.to_dict()
        param = json.loads(list_data[0]) if isinstance(list_data, list) else list_data
    if not param:
        abort(404)
    #if 'image' in request.files:
    #    param.update({'image': request.files['image']})
    message, status = service.create_slider(param,request.files['image'] if 'image' in request.files else None)
    return jsonify({'msg': message}), status

@sliders.route('/<id>', methods=['PATCH'])
#@cross_origin()
@permissions.has_permission(['slider.edit'])
def update_slider(self,id):
    if request.is_json:
        param = request.json
    else:
        dictionary = request.form.to_dict(flat=False)
        list = dictionary['form']
        param = json.loads(list[0])
    if not param:
        abort(404)
    #if 'image' in request.files:
    #    param.update({'image': request.files['image']})
    message, status = service.update_slider(id, param,request.files['image'] if 'image' in request.files else None)
    return jsonify({'msg': message}), status


@sliders.route('/<id>', methods=['DELETE'])
#@cross_origin()
@permissions.has_permission(['slider.delete'])
def delete_slider(self, id):
    message, status = service.delete_slider(id)
    return jsonify({'msg': message}), status



@sliders.route('/slider_types/', methods=['GET'])
#@cross_origin()
@permissions.has_permission(['slider_type.show'])
def get_all_slider_types(self):
    types, status = service.get_slider_types()
    return jsonify({'types': types}), status

@sliders.route('/slider_types/', methods=['POST'])
#@cross_origin()
@permissions.has_permission(['slider_type.add'])
def add_slider_type(self):
    if 'name' not in request.json:
        abort(404)
    message, status = service.create_slider_type(request.json)
    return jsonify({'msg': message}), status

@sliders.route('/slider_types/<name>', methods=['PATCH'])
#@cross_origin()
@permissions.has_permission(['slider_type.edit'])
def update_slider_type(self,name):
    if 'name' not in request.json:
        abort(404)
    message, status = service.update_slider_type(name, request.json)
    return jsonify({'msg': message}), status

@sliders.route('/slider_types/<name>', methods=['DELETE'])
#@cross_origin()
@permissions.has_permission(['slider_type.delete'])
def delete_slider_type(self, name):
    message, status = service.delete_slider_type(name)
    return jsonify({'msg': message}), status