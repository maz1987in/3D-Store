from flask import Blueprint, request, jsonify, abort
from app.rating.service import RatingService
from app.security import roles

__uri__ = 'ratings'
__blueprint__ = 'ratings'

ratings = Blueprint(__uri__, __name__)

service = RatingService()

@ratings.route('/', methods=['POST'])
@roles.token_required
def add_rating(self):
    if request.is_json:
        param = request.json
    else:
        abort(400, 'Request must be JSON')

    message, status = service.create_rating(param, self.id)
    return jsonify({'msg': message}), status

@ratings.route('/<product_id>', methods=['GET'])
def get_ratings(product_id):
    ratings, status = service.get_ratings(product_id)
    return jsonify(ratings), status

@ratings.route('/<id>', methods=['PATCH'])
@roles.token_required
def update_rating(self,id):
    if request.is_json:
        param = request.json
    else:
        abort(400, 'Request must be JSON')

    message, status = service.update_rating(id, param, self.id)
    return jsonify({'msg': message}), status

@ratings.route('/<id>', methods=['DELETE'])
@roles.token_required
def delete_rating(self,id):
    message, status = service.delete_rating(id, self.id)
    return jsonify({'msg': message}), status