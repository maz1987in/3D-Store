import uuid
import sqlalchemy as sql
from flask import current_app
from sqlalchemy_filters.pagination import apply_pagination
from app.common import filters_serialization
from app.common.error_handling import ResourceNotFoundError
from app.common.queries import create_filters, create_sorters, filter_and_sort_query
from app.utilities.common_utils import debug_return, print_dict_items, change_string_to_time
from app.utilities.request_utils import not_exisit_in_request
from .model import Invoice, InvoiceCounter
from config import BaseConfig
from app.utilities.db_utils import session_scope
from app.users.model import User
from app.customers.model import Customer
from app.branch.model import Branch
from datetime import timezone, datetime
from app.inventory.service import InventoryService
from app.utilities.error_utils import handle_errors  # Import the decorator

class InvoiceService:

    def get_invoices_model(self, invoices):
        if isinstance(invoices, list):
            result = []
            for invoice in invoices:
                data = {}
                if hasattr(invoice, 'Invoice'):
                    data['invoice'] = invoice.Invoice.json()
                if hasattr(invoice, 'Customer'):
                    data['customer'] = invoice.Customer.json() if invoice.Customer else None
                if hasattr(invoice, 'Branch'):
                    data['branch'] = invoice.Branch.json() if invoice.Branch else None
                result.append(data)
            return result
        else:
            result = []
            data = {}
            if hasattr(invoices, 'Invoice'):
                data['invoice'] = invoices.Invoice.json()
            else:
                data = invoices.json()
            if hasattr(invoices, 'Customer'):
                data['customer'] = invoices.Customer.json() if invoices.Customer else None
            if hasattr(invoices, 'Branch'):
                data['branch'] = invoices.Branch.json() if invoices.Branch else None
            result.append(data)
        return result

    @handle_errors("Invoice")
    def get_invoices(self, id, filter):
        with session_scope() as session:
            query = session.query(Invoice, Customer, Branch).filter(Invoice.customer_id == Customer.id, Invoice.branch_id == Branch.id)

            if id is None:
                if filter.sort is None:
                    filter.sorters = create_sorters('date', 'desc')

                query = filter_and_sort_query(filter.filters, filter.sorters, query, [Invoice, Customer, Branch])

                query, pagination = apply_pagination(query, page_number=int(filter.page), page_size=int(filter.per_page))
                invoices = query.all()
                result = {'invoices': self.get_invoices_model(invoices), 'filters': filters_serialization.get_pagination_serialization(pagination, filter.sort, filter.sort_order, filter.queries)}
            else:
                invoices = query.filter(Invoice.id == id).first()
                if invoices is None:
                    raise ResourceNotFoundError("Invoice")
                result = {'invoices': self.get_invoices_model(invoices)}

            return result, 200

    @handle_errors("Invoice")
    def get_invoices_by_id(self, id):
        with session_scope() as session:
            invoice = session.query(Invoice).filter(Invoice.id == id).first()
            if invoice is None:
                raise ResourceNotFoundError("Invoice")
            return self.get_invoices_model(invoice), 200

    @handle_errors("Invoice")
    def get_invoices_by_transaction_id(self, transaction_id):
        with session_scope() as session:
            invoice = session.query(Invoice).filter(Invoice.transaction_id == transaction_id).first()
            if invoice is None:
                raise ResourceNotFoundError("Invoice")
            return self.get_invoices_model(invoice), 200

    @handle_errors("Invoice")
    def get_invoices_by_user_id(self, user_id, filter):
        with session_scope() as session:
            query = session.query(Invoice).filter(Invoice.user_id == user_id)
            if filter.sort is None:
                filter.sorters = create_sorters('date', 'desc')

            query = filter_and_sort_query(filter.filters, filter.sorters, query, Invoice)

            query, pagination = apply_pagination(query, page_number=int(filter.page), page_size=int(filter.per_page))
            invoices = query.all()
            result = {'invoices': self.get_invoices_model(invoices), 'filters': filters_serialization.get_pagination_serialization(pagination, filter.sort, filter.sort_order, filter.queries)}

            return result, 200

    @handle_errors("Invoice")
    def create_invoice(self, data):
        with session_scope() as session:
            uuid_id = uuid.uuid4()
            invoice_number = self.generate_invoice_number(session)

            invoice = Invoice(
                id=str(uuid_id),
                number=invoice_number,
                total_amount=not_exisit_in_request(data, 'total_amount', None),
                discount=not_exisit_in_request(data, 'discount', None),
                tax=not_exisit_in_request(data, 'tax', None),
                delivery_amount=not_exisit_in_request(data, 'delivery_amount', None),
                grand_total=not_exisit_in_request(data, 'grand_total', None),
                customer_id=not_exisit_in_request(data, 'customer_id', None),
                branch_id=not_exisit_in_request(data, 'branch_id', None),
                user_id=not_exisit_in_request(data, 'user_id', None),
                payment_status=not_exisit_in_request(data, 'payment_status', 'pending'),
                date=change_string_to_time(data['date']),
                summary=not_exisit_in_request(data, 'summary', None),
            )  # type: ignore

            # Update the stock (reuse same session)
            service = InventoryService()
            items = data['summary']
            for item in items:
                inv_id = not_exisit_in_request(item, 'inventory_id', None)
                body = {
                    'quantity': item['quantity'],
                    'product_id': item['id'],
                    'branch_id': data['branch_id']
                }
                service.update_stock(inv_id, body, session=session)

            session.add(invoice)
            session.commit()

            return "Created", 201, str(uuid_id)

    def generate_invoice_number(self, session):
        counter = session.query(InvoiceCounter).with_for_update().first()
        if not counter:
            counter = InvoiceCounter(last_number=0)
            session.add(counter)
            session.flush()  # get ID

        counter.last_number += 1
        session.flush()  # persist increment

        return f"INV-{counter.last_number:05d}"

    @handle_errors("Invoice")
    def create_invoice_refund(self, data):
        with session_scope() as session:
            uuid_id = uuid.uuid4()

            invoice = Invoice(
                id=str(uuid_id),
                number=not_exisit_in_request(data, 'number', None),
                total_amount=not_exisit_in_request(data, 'total_amount', None),
                discount=not_exisit_in_request(data, 'discount', None),
                tax=not_exisit_in_request(data, 'tax', None),
                delivery_amount=not_exisit_in_request(data, 'delivery_amount', None),
                grand_total=not_exisit_in_request(data, 'grand_total', None),
                customer_id=not_exisit_in_request(data, 'customer_id', None),
                branch_id=not_exisit_in_request(data, 'branch_id', None),
                user_id=not_exisit_in_request(data, 'user_id', None),
                payment_status=not_exisit_in_request(data, 'payment_status', 'pending'),
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

            session.add(invoice)
            session.commit()

            return "Created", 201, str(uuid_id)

    @handle_errors("Invoice")
    def update_invoice(self, id, data):
        with session_scope() as session:
            invoice = session.query(Invoice).filter(Invoice.id == id).first()

            invoice.number = not_exisit_in_request(data, 'number', invoice.number)
            invoice.total_amount = not_exisit_in_request(data, 'total_amount', invoice.total_amount)
            invoice.discount = not_exisit_in_request(data, 'discount', invoice.discount)
            invoice.tax = not_exisit_in_request(data, 'tax', invoice.tax)
            invoice.delivery_amount = not_exisit_in_request(data, 'tax', invoice.delivery_amount)
            invoice.grand_total = not_exisit_in_request(data, 'grand_total', invoice.grand_total)
            invoice.customer_id = not_exisit_in_request(data, 'customer_id', invoice.customer_id)
            invoice.branch_id = not_exisit_in_request(data, 'branch_id', invoice.branch_id)
            invoice.user_id = not_exisit_in_request(data, 'user_id', invoice.user_id)
            invoice.payment_status = not_exisit_in_request(data, 'payment_status', invoice.payment_status)
            invoice.date = not_exisit_in_request(data, 'date', invoice.date)
            invoice.summary = not_exisit_in_request(data, 'summary', invoice.summary)
            invoice.modified_date = datetime.now(timezone.utc)

            session.commit()

            return 'Invoice updated', 200

    @handle_errors("Invoice")
    def delete_invoice(self, id):
        with session_scope() as session:
            invoice = session.query(Invoice).filter(Invoice.id == id).first()

            if invoice is None:
                raise ResourceNotFoundError("Invoice")

            session.delete(invoice)
            session.commit()

            return "Invoice Deleted", 200

    @handle_errors("Invoice")
    def get_invoice_by_type_and_id_and_filter(self, model_type, model_id, filter):
        with session_scope() as session:
            query = session.query(Invoice)

            query = filter_and_sort_query(filter.filters, filter.sorters, query, Invoice)

            if model_id is None:
                query = query.filter_by(model_type=model_type)
            else:
                query = query.filter_by(model_type=model_type, model_id=model_id)

            query, pagination = apply_pagination(query, page_number=int(filter.page), page_size=int(filter.per_page))
            invoices = query.all()
            result = {'invoices': self.get_invoices_model(invoices), 'filters': filters_serialization.get_pagination_serialization(pagination, filter.sort, filter.sort_order, filter.queries)}

            return result, 200

    @handle_errors("Invoice")
    def get_invoice_by_type_and_id(self, model_type, model_id):
        with session_scope() as session:
            invoices = session.query(Invoice).filter_by(model_type=model_type, model_id=model_id).all()
            if invoices is None:
                raise ResourceNotFoundError("Invoice")
            return self.get_invoices_model(invoices), 200

    @handle_errors("Invoice")
    def get_invoices_total_amount(self, filter):
        with session_scope() as session:
            query = session.query(sql.func.sum(Invoice.grand_total).label('total_amount'))
            if filter:
                query = filter_and_sort_query(filter.filters, filter.sorters, query, Invoice)

            invoices = query.first()
            return invoices.total_amount, 200

    @handle_errors("Invoice")
    def get_invoices_by_customer_mobile(self, mobile, filter):
        with session_scope() as session:
            query = session.query(Invoice, Customer, Branch).filter(Invoice.customer_id == Customer.id, Invoice.branch_id == Branch.id)
            query = query.filter(Customer.mobile == mobile)
            query = filter_and_sort_query(filter.filters, filter.sorters, query, Invoice)

            query, pagination = apply_pagination(query, page_number=int(filter.page), page_size=int(filter.per_page))
            invoices = query.all()
            result = {'invoices': self.get_invoices_model(invoices), 'filters': filters_serialization.get_pagination_serialization(pagination, filter.sort, filter.sort_order, filter.queries)}

            return result, 200

    @handle_errors("Invoice")
    def get_total_invoices_count(self, filter=None):
        """
        Get the total number of invoices, optionally filtered by criteria.
        """
        with session_scope() as session:
            query = session.query(sql.func.count(Invoice.id))
            
            # Apply filters if provided
            if filter:
                query = filter_and_sort_query(filter.filters, filter.sorters, query, Invoice)

            total_count = query.scalar()
            return {'total_invoices_count': total_count or 0}, 200