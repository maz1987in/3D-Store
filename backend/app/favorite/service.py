## service layer of the API
import json
import uuid
import sqlalchemy as sql
from flask import current_app
from app.common.error_handling import ResourceNotFoundError
from app.utilities.common_utils import debug_return
from config import BaseConfig
from .model import Favorite
from datetime import datetime, timezone
from app.utilities.db_utils import session_scope
from app.utilities.error_utils import handle_errors  # Import the decorator

class FavoriteService:
    @handle_errors("Favorite")
    def get_all_favorites(self, id):
        with session_scope() as session:
            if id is None:
                favorites = session.query(Favorite).all()
            else:
                favorites = session.query(Favorite).filter_by(id=id).all()
            
            result = []

            for favorite in favorites:
                data = {
                    'id': favorite.id,
                    'model_type': favorite.model_type,
                    'model_id': favorite.model_id,
                    'user_id': favorite.user_id,
                    'create_date': favorite.create_date
                }
                result.append(data)

            return result

    @handle_errors("Favorite")
    def get_user_favorites(self, model_type, model_id, user_id):
        with session_scope() as session:
            query = session.query(Favorite)
            if model_type is not None:
                query = query.filter_by(model_type=model_type)
            if model_id is not None:
                query = query.filter_by(model_id=model_id)
            if user_id is not None:
                query = query.filter_by(user_id=user_id)
            favorites = query.all()
            result = []

            for favorite in favorites:
                data = {
                    'id': favorite.id,
                    'model_type': favorite.model_type,
                    'model_id': favorite.model_id,
                    'user_id': favorite.user_id,
                    'create_date': favorite.create_date
                }
                result.append(data)

            return result, 200

    @handle_errors("Favorite")
    def create_favorite(self, data):
        with session_scope() as session:
            query = session.query(Favorite)
            query = query.filter_by(model_type=data['model_type'])
            query = query.filter_by(model_id=data['model_id'])
            query = query.filter_by(user_id=data['user_id'])
            favorites = query.first()
            if favorites is not None:
                return 'Already exists', 409
            favorite = Favorite(
                id=uuid.uuid4(),
                model_type=data['model_type'], 
                model_id=data['model_id'], 
                user_id=data['user_id'],
                create_date=datetime.now(timezone.utc)
            )

            session.add(favorite)
            session.commit()
            return 'Favorite Created', 201

    @handle_errors("Favorite")
    def delete_favorite(self, id):
        with session_scope() as session:
            favorite = session.query(Favorite).filter_by(id=id).first()

            if favorite is None:
                raise ResourceNotFoundError("Favorite")
            
            session.delete(favorite)
            session.commit()

            return 'Favorite deleted', 200

    @handle_errors("Favorite")
    def delete_user_model_favorites(self, model_type, model_id, user_id, favorite_id):
        with session_scope() as session:
            query = session.query(Favorite)
            if model_type is not None:
                query = query.filter_by(model_type=model_type)
            if model_id is not None:
                query = query.filter_by(model_id=model_id)
            if user_id is not None:
                query = query.filter_by(user_id=user_id)
            if favorite_id is not None:
                query = query.filter_by(id=favorite_id)
            favorites = query.all()
            for favorite in favorites:
                session.delete(favorite)
            session.commit()
            return 'Favorite deleted', 200