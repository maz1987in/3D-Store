import os
from flask_cors import CORS, cross_origin
from flask import Blueprint, request, jsonify, abort, make_response, send_from_directory, g
from werkzeug.utils import secure_filename
from depot.manager import DepotManager
from datetime import datetime, timezone
from app.security import roles, permissions
from .service import FavoriteService

__uri__ = 'favorites'
__blueprint__ = 'favorites'

favorites = Blueprint(__uri__, __name__)

service = FavoriteService()

@favorites.route('/', methods=['GET'])
#@cross_origin()
@permissions.has_permission(['favorite.show.my', 'favorite.show.all'])
def get_favorites(self):
    favorites = service.get_all_favorites(None)
    return jsonify({'favorites': favorites})

@favorites.route('/<id>', methods=['GET'])
#@cross_origin()
@permissions.has_permission(['favorite.show.my', 'favorite.show.all'])
def get_favorite(self,id):
    favorites = service.get_all_favorites(id)
    return jsonify({'favorites': favorites})

@favorites.route('/filter/<user_id>', defaults={'model_id': None,'model_type': None}, methods=['GET'])
@favorites.route('/filter/<user_id>/<model_type>', defaults={'model_id': None}, methods=['GET'])
@favorites.route('/filter/<user_id>/<model_type>/<model_id>', methods=['GET'])
#@cross_origin()
@permissions.has_permission(['favorite.show.my', 'favorite.show.all'])
def get_favorite_by_filters(self,model_type=None, model_id=None, user_id=None):
    if 'favorite.show.my' in g.permission:
        model_id = self.id
    favorites = service.get_user_favorites(model_type,model_id,user_id)
    return jsonify({'favorites': favorites})

@favorites.route('/', methods=['POST'])
#@cross_origin()
@permissions.has_permission(['favorite.add'])
def add_favorite(self):
    request.json.update({'user_id':self.id})  
    message, status = service.create_favorite(request.json)
    return jsonify({'msg': message}), status

@favorites.route('/<int:id>', methods=['DELETE'])
#@cross_origin()
@permissions.has_permission(['favorite.delete'])
def delete_favorite(id):
    message, status = service.delete_favorite(id)
    return jsonify({'msg': message}), status