## service layer of the API
import json
import sqlalchemy as sql
from flask import current_app
from sqlalchemy_filters import apply_pagination, apply_sort
from app.utilities.common_utils import debug_return, validate_file_content
from app.utilities.db_utils import session_scope
from config import Config
from .model import Category
from app.common import filters_serialization
from app.common.queries import filter_and_sort_query
from app.utilities import request_utils
from datetime import datetime, timezone
import uuid
from app.common.error_handling import ResourceNotFoundError
from app.utilities.error_utils import handle_errors  # Import the decorator

ALLOWED_CONTENT_TYPES = {'image/svg+xml'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ['svg']

class CategoryService:
    def get_category_model(self, categories):
        if isinstance(categories, list):
            return [category.json() for category in categories]
        return categories.json()

    @handle_errors("Category")
    def get_categories(self, id, filter): 
        with session_scope() as session:
            query = session.query(Category)
            result = None
            if id is None:
                query = filter_and_sort_query(filter.filters, filter.sorters, query, Category)
                query, pagination = apply_pagination(query, page_number=int(filter.page), page_size=int(filter.per_page))
                categories = query.all()
                result = {
                    'categories': self.get_category_model(categories),
                    'filters': filters_serialization.get_pagination_serialization(
                        pagination, filter.sort, filter.sort_order, filter.queries
                    )
                }
            else:
                categories = query.filter_by(id=id).all()
                result = {'categories': self.get_category_model(categories)}

            return result

    @handle_errors("Category")
    def get_categories_all(self): 
        with session_scope() as session:
            query = session.query(Category)
            categories = query.all()
            result = {'categories': self.get_category_model(categories)}
            return result

    @handle_errors("Category")
    def get_categories_dependency(self, parent_id): 
        with session_scope() as session:
            query1 = session.query(Category)
            category = query1.filter_by(id=parent_id).all()

            if not category:
                raise ResourceNotFoundError("Category")

            query2 = session.query(Category)
            category_dependency = query2.filter_by(parent_id=parent_id).all()

            result = {
                'category': self.get_category_model(category),
                'dependencies': self.get_category_model(category_dependency)
            }
            return result

    @handle_errors("Category")
    def update_category(self, id, data, icon):
        with session_scope() as session:
            if icon and (not allowed_file(icon.filename) or not validate_file_content(icon, ALLOWED_CONTENT_TYPES)):
                return 'File type is not allowed', 400

            category = session.query(Category).filter_by(id=id).first()
            if category is None:
                raise ResourceNotFoundError("Category")

            if request_utils.is_exisit_in_request(data, 'parent_id'):
                category.parent_id = data['parent_id']
            category.enable = request_utils.str_to_bool(data, 'enable', False)
            category.order = data['order']
            category.css_class = request_utils.not_exisit_in_request(data, 'css_class')
            category.icon = icon
            category.timestamp = datetime.now(timezone.utc)

            for local in Config.AVAILABLE_LOCALES.keys():
                if isinstance(data['name'], str):
                    category.translations[local].name = json.loads(data['name'])[local]
                    category.translations[local].content = json.loads(data['content'])[local]
                else:
                    category.translations[local].name = data['name'][local]
                    category.translations[local].content = data['content'][local]

            session.commit()
            return 'Updated', 200

    @handle_errors("Category")
    def create_category(self, data, icon):
        with session_scope() as session:
            if icon and (not allowed_file(icon.filename) or not validate_file_content(icon, ALLOWED_CONTENT_TYPES)):
                return 'File type is not allowed', 400

            category = Category(
                id=uuid.uuid4(),
                order=data['order'],
                enable=request_utils.str_to_bool(data, 'enable', False),
                css_class=request_utils.not_exisit_in_request(data, 'css_class'),
                icon=icon,
                timestamp=datetime.now(timezone.utc)
            )
            if request_utils.is_exisit_in_request(data, 'parent_id') and data['parent_id'] != '':
                category.parent_id = request_utils.not_exisit_in_request(data, 'parent_id')

            for local in Config.AVAILABLE_LOCALES.keys():
                if isinstance(data['name'], str):
                    category.translations[local].name = json.loads(data['name'])[local]
                    category.translations[local].content = json.loads(data['content'])[local]
                else:
                    category.translations[local].name = data['name'][local]
                    category.translations[local].content = data['content'][local]

            session.add(category)
            session.commit()
            return 'Category Created', 201

    @handle_errors("Category")
    def delete_category(self, id):
        with session_scope() as session:
            category = session.query(Category).filter_by(id=id).first()

            if category is None:
                raise ResourceNotFoundError("Category")

            session.delete(category)
            session.commit()
            return 'Category deleted', 200