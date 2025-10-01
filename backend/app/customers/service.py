## service layer of the API
import json
import sqlalchemy as sql

from flask import current_app, jsonify
from sqlalchemy_filters import apply_pagination, apply_sort
from app.common.error_handling import ResourceNotFoundError
from app.utilities.common_utils import change_string_to_time, debug_return
from config import BaseConfig, Config
from .model import Customer
from app.common import filters_serialization
from app.common.queries import create_sorters, filter_and_sort_query, filter_query, create_filters
from app.utilities.request_utils import not_exisit_in_request
from datetime import date, datetime
import uuid
from app.utilities.db_utils import session_scope
from datetime import timezone
from app.utilities.error_utils import handle_errors  # Import the decorator

class CustomerService:
    def get_customer_model(self, customers):
        if isinstance(customers, list):
            return [customer.json() for customer in customers]
        return customers.json()

    @handle_errors("Customer")
    def get_customers(self, id, filter): 
        with session_scope() as session:
            query = session.query(Customer)
            result = None
            if id is None:
                if filter.sort is None:
                    filter.sorters = create_sorters('modified_date', 'desc')
                query = filter_and_sort_query(filter.filters, filter.sorters, query, Customer)

                query, pagination = apply_pagination(query, page_number=int(filter.page), page_size=int(filter.per_page))
                customers = query.all()
                result = {
                    'customers': self.get_customer_model(customers),
                    'filters': filters_serialization.get_pagination_serialization(
                        pagination, filter.sort, filter.sort_order, filter.queries
                    )
                }
            else:
                customers = query.filter_by(id=id).first()
                if customers is None:
                    raise ResourceNotFoundError("Customer")
                result = {'customers': self.get_customer_model(customers)}

            return result, 200

    @handle_errors("Customer")
    def create_customer(self, data):
        with session_scope() as session:
            customer = Customer(
                id=uuid.uuid4(),
                location=not_exisit_in_request(data, 'location', None),
                mobile=not_exisit_in_request(data, 'mobile', None),
                email=not_exisit_in_request(data, 'email', None),
                city=not_exisit_in_request(data, 'city', None),
                address=not_exisit_in_request(data, 'address', None),
                notes=not_exisit_in_request(data, 'notes', None),
                create_date=datetime.now(timezone.utc),
                modified_date=datetime.now(timezone.utc)
            )  # type: ignore
            for local in Config.AVAILABLE_LOCALES.keys():
                if isinstance(data['name'], str):
                    customer.translations[local].name = json.loads(data['name'])[local]
                else:
                    customer.translations[local].name = data['name'][local]

            session.add(customer)
            session.commit()

            return 'Customer Created', 201

    @handle_errors("Customer")
    def update_customer(self, id, data):
        with session_scope() as session:
            customer = session.query(Customer).filter_by(id=id).first()
            if customer is None:
                raise ResourceNotFoundError("Customer")
            customer.location = not_exisit_in_request(data, 'location', customer.location)
            customer.mobile = not_exisit_in_request(data, 'mobile', customer.mobile)
            customer.email = not_exisit_in_request(data, 'email', customer.email)
            customer.city = not_exisit_in_request(data, 'city', customer.city)
            customer.address = not_exisit_in_request(data, 'address', customer.address)
            customer.notes = not_exisit_in_request(data, 'notes', customer.notes)
            customer.modified_date = datetime.now(timezone.utc)
            for local in Config.AVAILABLE_LOCALES.keys():
                if isinstance(data['name'], str):
                    customer.translations[local].name = json.loads(data['name'])[local]
                else:
                    customer.translations[local].name = data['name'][local]
            session.commit()

            return 'Updated', 200

    @handle_errors("Customer")
    def delete_customer(self, id):
        with session_scope() as session:
            customer = session.query(Customer).filter_by(id=id).first()

            if customer is None:
                raise ResourceNotFoundError("Customer")

            session.delete(customer)
            session.commit()

            return 'Customer deleted', 200

    @handle_errors("Customer")
    def get_total_customers(self):
        """
        Get the total number of customers.
        """
        with session_scope() as session:
            total_customers = session.query(sql.func.count(Customer.id)).scalar()
            return {'total_customers': total_customers}, 200
