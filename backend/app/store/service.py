## service layer of the API
import json
import sqlalchemy as sql

from flask import current_app
from sqlalchemy_filters import apply_pagination, apply_sort
from app.common.error_handling import ResourceNotFoundError
from app.utilities.common_utils import change_string_to_time, debug_return
from config import Config
from .model import Store
from app.common import filters_serialization
from app.common.queries import create_sorters, filter_and_sort_query
from app.utilities.request_utils import not_exisit_in_request
from datetime import datetime, timezone
import uuid
from app.utilities.db_utils import session_scope
from app.utilities.error_utils import handle_errors  # Import the decorator

class StoreService:
    def get_store_model(self, stores):
        if isinstance(stores, list):
            return [store.json() for store in stores]
        return stores.json()

    @handle_errors("Store")
    def get_stores(self, id, filter): 
        with session_scope() as session:
            query = session.query(Store)
            result = None
            if id is None:
                if filter.sort is None:
                    filter.sorters = create_sorters('modified_date', 'desc')
                query = filter_and_sort_query(filter.filters, filter.sorters, query, Store)

                query, pagination = apply_pagination(query, page_number=int(filter.page), page_size=int(filter.per_page))
                stores = query.all()
                result = {'stores': self.get_store_model(stores), 'filters': filters_serialization.get_pagination_serialization(pagination, filter.sort, filter.sort_order, filter.queries)}
            else:
                stores = query.filter_by(id=id).first()
                if stores is None:
                    raise ResourceNotFoundError("Store")
                result = {'stores': self.get_store_model(stores)}

            return result, 200

    @handle_errors("Store")
    def create_store(self, data):
        with session_scope() as session:
            store = Store(
                id=uuid.uuid4(),
                location=data['location'],
                manager=data['manager'],
                create_date=datetime.now(timezone.utc),
                modified_date=datetime.now(timezone.utc)
            )  # type: ignore
            for local in Config.AVAILABLE_LOCALES.keys():
                if isinstance(data['name'], str):
                    store.translations[local].name = json.loads(data['name'])[local]
                else:
                    store.translations[local].name = data['name'][local]

            session.add(store)
            session.commit()

            return 'Store Created', 201

    @handle_errors("Store")
    def update_store(self, id, data):
        with session_scope() as session:
            store = session.query(Store).filter_by(id=id).first()
            if store is None:
                raise ResourceNotFoundError("Store")
            store.location = not_exisit_in_request(data, 'location', store.location)
            store.manager = not_exisit_in_request(data, 'manager', store.manager)
            store.modified_date = datetime.now(timezone.utc)
            for local in Config.AVAILABLE_LOCALES.keys():
                if isinstance(data['name'], str):
                    store.translations[local].name = json.loads(data['name'])[local]
                else:
                    store.translations[local].name = data['name'][local]
            session.commit()

            return 'Updated', 200

    @handle_errors("Store")
    def delete_store(self, id):
        with session_scope() as session:
            store = session.query(Store).filter_by(id=id).first()

            if store is None:
                raise ResourceNotFoundError("Store")

            session.delete(store)
            session.commit()

            return 'Store deleted', 200
