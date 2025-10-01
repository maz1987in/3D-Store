## service layer of the API
import json
import sqlalchemy as sql

from flask import current_app
from sqlalchemy_filters import apply_pagination, apply_sort
from app.common.error_handling import ResourceNotFoundError
from app.utilities.common_utils import change_string_to_time, debug_return
from config import Config
from .model import Labor, LaborCategory
from app.common import filters_serialization
from app.common.queries import create_sorters, filter_and_sort_query
from app.utilities.request_utils import not_exisit_in_request
from datetime import datetime, timezone
import uuid
from app.utilities.db_utils import session_scope
from app.utilities.error_utils import handle_errors  # Import the decorator

class LaborService:
    def get_labor_model(self, labors):
        result = []
        if isinstance(labors, list):
            for labor in labors:
                result.append(labor.json())
            return result
        else:
            return labors.json()

    @handle_errors("Labor")
    def get_labors(self, id, filter): 
        with session_scope() as session:
            query = session.query(Labor).join(LaborCategory, Labor.category_id == LaborCategory.id)
            result = None
            if id is None:
                if filter.sort is None:
                    filter.sorters = create_sorters('modified_date', 'desc')
                query = filter_and_sort_query(filter.filters, filter.sorters, query, [Labor, LaborCategory])

                query, pagination = apply_pagination(query, page_number=int(filter.page), page_size=int(filter.per_page))
                labors = query.all()
                result = {'labors': self.get_labor_model(labors), 'filters': filters_serialization.get_pagination_serialization(pagination, filter.sort, filter.sort_order, filter.queries)}
            else:
                labors = query.filter_by(id=id).first()
                if labors is None:
                    raise ResourceNotFoundError("Labor")
                result = {'labors': self.get_labor_model(labors)}

            return result, 200

    @handle_errors("Labor")
    def get_labors_f(self, filter): 
        with session_scope() as session:
            query = session.query(Labor).join(LaborCategory, Labor.category_id == LaborCategory.id)
            
            if filter.sort is None:
                filter.sorters = create_sorters('modified_date', 'desc')
            query = filter_and_sort_query(filter.filters, filter.sorters, query, [Labor, LaborCategory])

            query, pagination = apply_pagination(query, page_number=int(filter.page), page_size=int(filter.per_page))
            labors = query.all()
            result = {'labors': self.get_labor_model(labors), 'filters': filters_serialization.get_pagination_serialization(pagination, filter.sort, filter.sort_order, filter.queries)}
            
            result = {'labors': self.get_labor_model(labors)}
            return result, 200

    @handle_errors("Labor")
    def create_labor(self, data):
        with session_scope() as session:
            labor = Labor(
                id=uuid.uuid4(),
                code=not_exisit_in_request(data, 'code', None),
                name=not_exisit_in_request(data, 'name', None),
                category_id=not_exisit_in_request(data, 'category_id', None),
                unit=not_exisit_in_request(data, 'unit', 'hour'),
                unit_price=not_exisit_in_request(data, 'unit_price', 0.0),
                description=not_exisit_in_request(data, 'description', None),
                status=not_exisit_in_request(data, 'status', 'APPROVED'),
                create_date=datetime.now(timezone.utc),
                modified_date=datetime.now(timezone.utc)
            )  # type: ignore
            session.add(labor)
            session.commit()
            return 'Labor Created', 201

    @handle_errors("Labor")
    def update_labor(self, id, data):
        with session_scope() as session:
            labor = session.query(Labor).filter_by(id=id).first()
            if labor is None:
                raise ResourceNotFoundError("Labor")
            labor.code = not_exisit_in_request(data, 'code', labor.code)
            labor.name = not_exisit_in_request(data, 'name', labor.name)
            labor.category_id = not_exisit_in_request(data, 'category_id', labor.category_id)
            labor.unit = not_exisit_in_request(data, 'unit', labor.unit)
            labor.unit_price = not_exisit_in_request(data, 'unit_price', labor.unit_price)
            labor.description = not_exisit_in_request(data, 'description', labor.description)
            labor.status = not_exisit_in_request(data, 'status', labor.status)
            labor.modified_date = datetime.now(timezone.utc)
            session.commit()
            return 'Updated', 200

    @handle_errors("Labor")
    def delete_labor(self, id):
        with session_scope() as session:
            labor = session.query(Labor).filter_by(id=id).first()
            if labor is None:
                raise ResourceNotFoundError("Labor")
            session.delete(labor)
            session.commit()
            return 'Labor deleted', 200

    def get_labor_category_model(self, categories):
        if isinstance(categories, list):
            result = [category.json() for category in categories]
        else:
            result = categories.json()
        return result

    @handle_errors("LaborCategory")
    def get_labor_categories(self, id, filter): 
        with session_scope() as session:
            query = session.query(LaborCategory)
            result = None
            if id is None:
                if filter.sort is None:
                    filter.sorters = create_sorters('modified_date', 'desc')
                query = filter_and_sort_query(filter.filters, filter.sorters, query, LaborCategory)

                query, pagination = apply_pagination(query, page_number=int(filter.page), page_size=int(filter.per_page))
                categories = query.all()
                result = {'categories': self.get_labor_category_model(categories), 'filters': filters_serialization.get_pagination_serialization(pagination, filter.sort, filter.sort_order, filter.queries)}
            else:
                categories = query.filter_by(id=id).all()
                result = {'categories': self.get_labor_category_model(categories)}

            return result, 200

    @handle_errors("LaborCategory")
    def create_labor_category(self, data):
        with session_scope() as session:
            category = LaborCategory(
                id=uuid.uuid4(),
                parent_id=not_exisit_in_request(data, 'parent_id', None),
                order=not_exisit_in_request(data, 'order', 0)
            )  # type: ignore
            for local in Config.AVAILABLE_LOCALES.keys():
                if isinstance(data['name'], str):
                    category.translations[local].name = json.loads(data['name'])[local]
                    category.translations[local].content = json.loads(data['content'])[local]
                else:
                    category.translations[local].name = data['name'][local]
                    category.translations[local].content = data['content'][local]
            session.add(category)
            session.commit()
            return 'Labor Category Created', 201

    @handle_errors("LaborCategory")
    def update_labor_category(self, id, data):
        with session_scope() as session:
            category = session.query(LaborCategory).filter_by(id=id).first()
            if category is None:
                raise ResourceNotFoundError("LaborCategory")
            category.parent_id = not_exisit_in_request(data, 'parent_id', category.parent_id)
            category.order = not_exisit_in_request(data, 'order', category.order)
            category.modified_date = datetime.now(timezone.utc)
            for local in Config.AVAILABLE_LOCALES.keys():
                if isinstance(data['name'], str):
                    category.translations[local].name = json.loads(data['name'])[local]
                    category.translations[local].content = json.loads(data['content'])[local]
                else:
                    category.translations[local].name = data['name'][local]
                    category.translations[local].content = data['content'][local]
            session.commit()
            return 'Updated', 200

    @handle_errors("LaborCategory")
    def delete_labor_category(self, id):
        with session_scope() as session:
            category = session.query(LaborCategory).filter_by(id=id).first()
            if category is None:
                raise ResourceNotFoundError("LaborCategory")
            session.delete(category)
            session.commit()
            return 'Labor Category deleted', 200
