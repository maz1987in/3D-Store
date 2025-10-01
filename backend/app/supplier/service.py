## service layer of the API
import json
import sqlalchemy as sql

from flask import current_app
from sqlalchemy_filters import apply_pagination, apply_sort
from app.common.error_handling import ResourceNotFoundError
from app.utilities.common_utils import change_string_to_time, debug_return
from config import BaseConfig, Config
from .model import Supplier
from app.common import filters_serialization
from app.common.queries import create_sorters, filter_and_sort_query, filter_query, create_filters
from app.utilities.request_utils import not_exisit_in_request
from datetime import date, datetime, timezone
import uuid
from app.utilities.db_utils import session_scope
from app.utilities.error_utils import handle_errors  # Import the decorator

class SupplierService:
    def get_supplier_model(self, suppliers):
        if isinstance(suppliers, list):
            return [supplier.json() for supplier in suppliers]
        return suppliers.json()

    @handle_errors("Supplier")
    def get_suppliers(self, id, filter): 
        with session_scope() as session:
            query = session.query(Supplier)
            result = None
            if id is None:
                if filter.sort is None:
                    filter.sorters = create_sorters('modified_date', 'desc')
                query = filter_and_sort_query(filter.filters, filter.sorters, query, Supplier)

                query, pagination = apply_pagination(query, page_number=int(filter.page), page_size=int(filter.per_page))
                suppliers = query.all()
                result = {'suppliers': self.get_supplier_model(suppliers), 'filters': filters_serialization.get_pagination_serialization(pagination, filter.sort, filter.sort_order, filter.queries)}
            else:
                suppliers = query.filter_by(id=id).first()
                if suppliers is None:
                    raise ResourceNotFoundError("Supplier")
                result = {'suppliers': self.get_supplier_model(suppliers)}

            return result, 200

    @handle_errors("Supplier")
    def create_supplier(self, data):
        with session_scope() as session:
            supplier = Supplier(
                id=uuid.uuid4(),
                name=not_exisit_in_request(data, 'name', None),
                phone=not_exisit_in_request(data, 'phone', None),
                email=not_exisit_in_request(data, 'email', None),
                address=not_exisit_in_request(data, 'address', None),
                details=not_exisit_in_request(data, 'details', None),
                create_date=datetime.now(timezone.utc),
                modified_date=datetime.now(timezone.utc)
            )  # type: ignore

            session.add(supplier)
            session.commit()

            return 'Supplier Created', 201

    @handle_errors("Supplier")
    def update_supplier(self, id, data):
        with session_scope() as session:
            supplier = session.query(Supplier).filter_by(id=id).first()
            if supplier is None:
                raise ResourceNotFoundError("Supplier")
            supplier.name = not_exisit_in_request(data, 'name', supplier.name)
            supplier.phone = not_exisit_in_request(data, 'phone', supplier.phone)
            supplier.email = not_exisit_in_request(data, 'email', supplier.email)
            supplier.address = not_exisit_in_request(data, 'address', supplier.address)
            supplier.details = not_exisit_in_request(data, 'details', supplier.details)
            supplier.modified_date = datetime.now(timezone.utc)

            session.commit()

            return 'Updated', 200

    @handle_errors("Supplier")
    def delete_supplier(self, id):
        with session_scope() as session:
            supplier = session.query(Supplier).filter_by(id=id).first()

            if supplier is None:
                raise ResourceNotFoundError("Supplier")
            
            session.delete(supplier)
            session.commit()

            return 'Supplier deleted', 200
