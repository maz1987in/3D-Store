## service layer of the API
import json
import sqlalchemy as sql
from sqlalchemy.orm.attributes import flag_modified
from flask import current_app
from sqlalchemy_filters import apply_pagination, apply_sort
from app.common.error_handling import ResourceNotFoundError
from app.medias.service import MediaService
from app.utilities.common_utils import change_string_to_time, debug_return
from config import BaseConfig, Config
from app.common import filters_serialization
from app.common.queries import create_sorters, filter_and_sort_query
from app.utilities.request_utils import not_exisit_in_request
from datetime import datetime, timezone
import uuid
from app.utilities.db_utils import session_scope
from app.category.model import Category
from app.utilities.file_upload_utils import upload_files, reindex_media
from app.utilities.error_utils import handle_errors  # Import the decorator
from app.rating.model import Rating  # Import the Rating model
from sqlalchemy import func

class RatingService:
    @handle_errors("Rating")
    def create_rating(self, data, user_id):
        score = data['score']
        if not (1 <= score <= 5):
            return 'Rating score must be between 1 and 5', 400

        with session_scope() as session:
            # Check if the user has already rated this product
            existing = session.query(Rating).filter_by(
                product_id=data['product_id'],
                user_id=user_id
            ).first()
            if existing:
                return 'User has already rated this product', 400

            rating = Rating(
                id=uuid.uuid4(),
                product_id=data['product_id'],
                user_id=user_id,
                score=score,
                comment=data.get('comment', None)
            )
            session.add(rating)
            session.commit()
            return 'Rating Created', 201

    @handle_errors("Rating")
    def get_ratings(self, product_id):
        with session_scope() as session:
            ratings = session.query(Rating).filter_by(product_id=product_id).all()
            return [rating.json() for rating in ratings], 200

    @handle_errors("Rating")
    def update_rating(self, id, data, user_id):
        score = data.get('score')
        if score is not None and not (1 <= score <= 5):
            return 'Rating score must be between 1 and 5', 400

        with session_scope() as session:
            rating = session.query(Rating).filter_by(id=id, user_id=user_id).first()
            if rating is None:
                raise ResourceNotFoundError("Rating")
            if score is not None:
                rating.score = score
            rating.comment = data.get('comment', rating.comment)
            session.commit()
            return 'Rating Updated', 200

    @handle_errors("Rating")
    def delete_rating(self, id):
        with session_scope() as session:
            rating = session.query(Rating).filter_by(id=id).first()
            if rating is None:
                raise ResourceNotFoundError("Rating")
            session.delete(rating)
            session.commit()
            return 'Rating Deleted', 200

    @handle_errors("Rating")
    def get_average_rating(self, product_id):
        with session_scope() as session:
            avg_score = session.query(func.avg(Rating.score)).filter_by(product_id=product_id).scalar()
            if avg_score is None:
                return {'average': 0, 'max': 5}, 200
            return {'average': round(float(avg_score), 2), 'max': 5}, 200