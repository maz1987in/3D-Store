import uuid
import sqlalchemy as sql
from flask import current_app
from sqlalchemy_filters.pagination import apply_pagination
from app.common import filters_serialization
from app.common.error_handling import ResourceNotFoundError
from app.common.queries import create_filters, create_sorters, filter_and_sort_query
from app.utilities.common_utils import debug_return, print_dict_items, change_string_to_time
from app.utilities.request_utils import not_exisit_in_request
from .model import Quotation
from config import BaseConfig
from app.utilities.db_utils import session_scope
from app.users.model import User
from app.customers.model import Customer
from app.branch.model import Branch
from datetime import timezone, datetime
from app.inventory.service import InventoryService
from app.utilities.error_utils import handle_errors  # Import the decorator

class QuotationService:

    def get_quotations_model(self, quotations):
        if isinstance(quotations, list):
            result = []
            for quotation in quotations:
                data = {}
                if hasattr(quotation, 'Quotation'):
                    data['quotation'] = quotation.Quotation.json()
                if hasattr(quotation, 'Customer'):
                    data['customer'] = quotation.Customer.json() if quotation.Customer else None
                if hasattr(quotation, 'Branch'):
                    data['branch'] = quotation.Branch.json() if quotation.Branch else None
                result.append(data)
            return result
        else:
            result = []
            data = {}
            if hasattr(quotations, 'Quotation'):
                data['quotation'] = quotations.Quotation.json()
            else:
                data = quotations.json()
            if hasattr(quotations, 'Customer'):
                data['customer'] = quotations.Customer.json() if quotations.Customer else None
            if hasattr(quotations, 'Branch'):
                data['branch'] = quotations.Branch.json() if quotations.Branch else None
            result.append(data)
        return result

    @handle_errors("Quotation")
    def get_quotations(self, id, filter):
        with session_scope() as session:
            query = session.query(Quotation, Customer, Branch).filter(Quotation.customer_id == Customer.id, Quotation.branch_id == Branch.id)

            if id is None:
                if filter.sort is None:
                    filter.sorters = create_sorters('date', 'desc')

                query = filter_and_sort_query(filter.filters, filter.sorters, query, [Quotation, Customer, Branch])

                query, pagination = apply_pagination(query, page_number=int(filter.page), page_size=int(filter.per_page))
                quotations = query.all()
                result = {'quotations': self.get_quotations_model(quotations), 'filters': filters_serialization.get_pagination_serialization(pagination, filter.sort, filter.sort_order, filter.queries)}
            else:
                quotations = query.filter(Quotation.id == id).first()
                if quotations is None:
                    raise ResourceNotFoundError("Quotation")
                result = {'quotations': self.get_quotations_model(quotations)}

            return result, 200

    @handle_errors("Quotation")
    def get_quotations_by_id(self, id):
        with session_scope() as session:
            quotation = session.query(Quotation).filter(Quotation.id == id).first()
            if quotation is None:
                raise ResourceNotFoundError("Quotation")
            return self.get_quotations_model(quotation), 200

    @handle_errors("Quotation")
    def get_quotations_by_transaction_id(self, transaction_id):
        with session_scope() as session:
            quotation = session.query(Quotation).filter(Quotation.transaction_id == transaction_id).first()
            if quotation is None:
                raise ResourceNotFoundError("Quotation")
            return self.get_quotations_model(quotation), 200

    @handle_errors("Quotation")
    def get_quotations_by_user_id(self, user_id, filter):
        with session_scope() as session:
            query = session.query(Quotation).filter(Quotation.user_id == user_id)
            if filter.sort is None:
                filter.sorters = create_sorters('date', 'desc')

            query = filter_and_sort_query(filter.filters, filter.sorters, query, Quotation)

            query, pagination = apply_pagination(query, page_number=int(filter.page), page_size=int(filter.per_page))
            quotations = query.all()
            result = {'quotations': self.get_quotations_model(quotations), 'filters': filters_serialization.get_pagination_serialization(pagination, filter.sort, filter.sort_order, filter.queries)}

            return result, 200

    @handle_errors("Quotation")
    def create_quotation(self, data):
        with session_scope() as session:
            uuid_id = uuid.uuid4()

            quotation = Quotation(
                id=str(uuid_id),
                number=not_exisit_in_request(data, 'number', None),
                total_amount=not_exisit_in_request(data, 'total_amount', None),
                discount=not_exisit_in_request(data, 'discount', None),
                tax=not_exisit_in_request(data, 'tax', None),
                grand_total=not_exisit_in_request(data, 'grand_total', None),
                customer_id=not_exisit_in_request(data, 'customer_id', None),
                branch_id=not_exisit_in_request(data, 'branch_id', None),
                user_id=not_exisit_in_request(data, 'user_id', None),
                qoute_status=not_exisit_in_request(data, 'qoute_status', 'pending'),
                date=change_string_to_time(data['date']),
                summary=not_exisit_in_request(data, 'summary', None),
            )  # type: ignore

            # Update the stock
            """
            service = InventoryService()
            items = data['summary']
            for item in items:
                id = not_exisit_in_request(item, 'inventory_id', None)
                body = {'quantity': item['quantity'], 'product_id': item['id'], 'branch_id': data['branch_id']}
                service.update_stock(id, body)
            """
            session.add(quotation)
            session.commit()

            return "Created", 201, str(uuid_id)
    """
    @handle_errors("Quotation")
    def create_quotation_refund(self, data):
        with session_scope() as session:
            uuid_id = uuid.uuid4()

            quotation = Quotation(
                id=str(uuid_id),
                number=not_exisit_in_request(data, 'number', None),
                total_amount=not_exisit_in_request(data, 'total_amount', None),
                discount=not_exisit_in_request(data, 'discount', None),
                tax=not_exisit_in_request(data, 'tax', None),
                grand_total=not_exisit_in_request(data, 'grand_total', None),
                customer_id=not_exisit_in_request(data, 'customer_id', None),
                branch_id=not_exisit_in_request(data, 'branch_id', None),
                user_id=not_exisit_in_request(data, 'user_id', None),
                qoute_status=not_exisit_in_request(data, 'qoute_status', 'pending'),
                date=change_string_to_time(data['date']),
                summary=not_exisit_in_request(data, 'summary', None),
            )  # type: ignore

            # Update the stock
            service = InventoryService()
            items = data['summary']
            for item in items:
                id = not_exisit_in_request(item, 'inventory_id', None)
                body = {'quantity': item['quantity'], 'product_id': item['id'], 'branch_id': data['branch_id']}
                service.update_stock_refund(id, body)

            session.add(quotation)
            session.commit()

            return "Created", 201, str(uuid_id)
    """
    @handle_errors("Quotation")
    def update_quotation(self, id, data):
        with session_scope() as session:
            quotation = session.query(Quotation).filter(Quotation.id == id).first()

            quotation.number = not_exisit_in_request(data, 'number', quotation.number)
            quotation.total_amount = not_exisit_in_request(data, 'total_amount', quotation.total_amount)
            quotation.discount = not_exisit_in_request(data, 'discount', quotation.discount)
            quotation.tax = not_exisit_in_request(data, 'tax', quotation.tax)
            quotation.grand_total = not_exisit_in_request(data, 'grand_total', quotation.grand_total)
            quotation.customer_id = not_exisit_in_request(data, 'customer_id', quotation.customer_id)
            quotation.branch_id = not_exisit_in_request(data, 'branch_id', quotation.branch_id)
            quotation.user_id = not_exisit_in_request(data, 'user_id', quotation.user_id)
            quotation.qoute_status = not_exisit_in_request(data, 'qoute_status', quotation.qoute_status)
            quotation.date = not_exisit_in_request(data, 'date', quotation.date)
            quotation.summary = not_exisit_in_request(data, 'summary', quotation.summary)
            quotation.modified_date = datetime.now(timezone.utc)

            session.commit()

            return 'Quotation updated', 200

    @handle_errors("Quotation")
    def delete_quotation(self, id):
        with session_scope() as session:
            quotation = session.query(Quotation).filter(Quotation.id == id).first()

            if quotation is None:
                raise ResourceNotFoundError("Quotation")

            session.delete(quotation)
            session.commit()

            return "Quotation Deleted", 200

    @handle_errors("Quotation")
    def get_quotation_by_type_and_id_and_filter(self, model_type, model_id, filter):
        with session_scope() as session:
            query = session.query(Quotation)

            query = filter_and_sort_query(filter.filters, filter.sorters, query, Quotation)

            if model_id is None:
                query = query.filter_by(model_type=model_type)
            else:
                query = query.filter_by(model_type=model_type, model_id=model_id)

            query, pagination = apply_pagination(query, page_number=int(filter.page), page_size=int(filter.per_page))
            quotations = query.all()
            result = {'quotations': self.get_quotations_model(quotations), 'filters': filters_serialization.get_pagination_serialization(pagination, filter.sort, filter.sort_order, filter.queries)}

            return result, 200

    @handle_errors("Quotation")
    def get_quotation_by_type_and_id(self, model_type, model_id):
        with session_scope() as session:
            quotations = session.query(Quotation).filter_by(model_type=model_type, model_id=model_id).all()
            if quotations is None:
                raise ResourceNotFoundError("Quotation")
            return self.get_quotations_model(quotations), 200

    @handle_errors("Quotation")
    def get_quotations_total_amount(self, filter):
        with session_scope() as session:
            query = session.query(sql.func.sum(Quotation.grand_total).label('total_amount'))
            if filter:
                query = filter_and_sort_query(filter.filters, filter.sorters, query, Quotation)

            quotations = query.first()
            return quotations.total_amount, 200

    @handle_errors("Quotation")
    def get_quotations_by_customer_mobile(self, mobile, filter):
        with session_scope() as session:
            query = session.query(Quotation, Customer, Branch).filter(Quotation.customer_id == Customer.id, Quotation.branch_id == Branch.id)
            query = query.filter(Customer.mobile == mobile)
            query = filter_and_sort_query(filter.filters, filter.sorters, query, Quotation)

            query, pagination = apply_pagination(query, page_number=int(filter.page), page_size=int(filter.per_page))
            quotations = query.all()
            result = {'quotations': self.get_quotations_model(quotations), 'filters': filters_serialization.get_pagination_serialization(pagination, filter.sort, filter.sort_order, filter.queries)}

            return result, 200

    @handle_errors("Quotation")
    def get_total_quotations_count(self, filter=None):
        """
        Get the total number of quotations, optionally filtered by criteria.
        """
        with session_scope() as session:
            query = session.query(sql.func.count(Quotation.id))
            
            # Apply filters if provided
            if filter:
                query = filter_and_sort_query(filter.filters, filter.sorters, query, Quotation)

            total_count = query.scalar()
            return {'total_quotations_count': total_count or 0}, 200