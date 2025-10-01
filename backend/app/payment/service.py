## service layer of the API
import json
import sqlalchemy as sql
from sqlalchemy.orm.attributes import flag_modified
from flask import current_app, jsonify
from sqlalchemy_filters import apply_pagination, apply_sort
from app.common.error_handling import ResourceNotFoundError
from app.utilities.common_utils import change_string_to_time, debug_return
from config import BaseConfig, Config
from .model import Payment
from app.common import filters_serialization
from app.common.queries import create_sorters, filter_and_sort_query
from app.utilities.request_utils import not_exisit_in_request
from datetime import datetime, timezone
import uuid
from app.utilities.db_utils import session_scope
from app.invoices.model import Invoice
from app.utilities.error_utils import handle_errors  # Import the decorator

class PaymentService:
    def get_payment_model(self, payments):
        result = []
        if isinstance(payments, list):
            for payment in payments:
                data = {}
                if hasattr(payment, 'Payment'):
                    data['payment'] = payment.Payment.json()
                else:
                    data['payment'] = payment.json()
                if hasattr(payment, 'Invoice'):
                    data['invoice'] = payment.Invoice.json() if payment.Invoice else None
                result.append(data)
            return result
        else:
            data = {}
            if hasattr(payments, 'Payment'):
                data['payment'] = payments.Payment.json()
            else:
                data['payment'] = payments.json()
            if hasattr(payments, 'Invoice'):
                data['invoice'] = payments.Invoice.json() if payments.Invoice else None
            return data

    @handle_errors("Payment")
    def get_payments(self, id, filter): 
        with session_scope() as session:
            query = session.query(Payment, Invoice).filter(Payment.invoice_id == Invoice.id)
            result = None
            if id is None:
                if filter.sort is None:
                    filter.sorters = create_sorters('modified_date', 'desc')
                query = filter_and_sort_query(filter.filters, filter.sorters, query, Payment)

                query, pagination = apply_pagination(query, page_number=int(filter.page), page_size=int(filter.per_page))
                payments = query.all()
                result = {'payments': self.get_payment_model(payments), 'filters': filters_serialization.get_pagination_serialization(pagination, filter.sort, filter.sort_order, filter.queries)}
            else:
                payments = query.filter_by(id=id).first()
                if payments is None:
                    raise ResourceNotFoundError("Payment")
                result = {'payments': self.get_payment_model(payments)}

            return result, 200

    @handle_errors("Payment")
    def get_payment_by_invoice_id(self, id):
        with session_scope() as session:
            query = session.query(Payment, Invoice).filter(Payment.invoice_id == Invoice.id)
            payments = query.filter(Payment.invoice_id == id).all()
            return self.get_payment_model(payments), 200

    @handle_errors("Payment")
    def create_payment(self, data):
        with session_scope() as session:
            payment_id = uuid.uuid4()
            payment = Payment(
                id=payment_id,
                invoice_id=data['invoice_id'],
                payment_method=data['payment_method'],
                amount_paid=data['amount_paid'],
                payment_date=change_string_to_time(data['payment_date']),
                create_date=datetime.now(timezone.utc),
                modified_date=datetime.now(timezone.utc)
            )  # type: ignore

            session.add(payment)
            session.commit()
            return 'Payment Created', 201

    @handle_errors("Payment")
    def update_payment(self, id, data, files):
        with session_scope() as session:
            payment = session.query(Payment).filter_by(id=id).first()
            if payment is None:
                raise ResourceNotFoundError("Payment")
            payment.invoice_id = not_exisit_in_request(data, 'invoice_id', payment.invoice_id)
            payment.payment_method = not_exisit_in_request(data, 'payment_method', payment.payment_method)
            payment.amount_paid = not_exisit_in_request(data, 'amount_paid', payment.amount_paid)
            payment.payment_date = not_exisit_in_request(data, 'payment_date', payment.payment_date)
            payment.modified_date = datetime.now(timezone.utc)

            session.commit()
            return 'Updated', 200

    @handle_errors("Payment")
    def delete_payment(self, id):
        with session_scope() as session:
            payment = session.query(Payment).filter_by(id=id).first()

            if payment is None:
                raise ResourceNotFoundError("Payment")
            
            session.delete(payment)
            session.commit()

            return 'Payment deleted', 200

    @handle_errors("Payment")
    def get_total_payments_amount(self, filter=None):
        """
        Get the total amount of all payments, optionally filtered by criteria.
        """
        with session_scope() as session:
            query = session.query(sql.func.sum(Payment.amount_paid))
            
            # Apply filters if provided
            if filter:
                query = filter_and_sort_query(filter.filters, filter.sorters, query, Payment)

            total_amount = query.scalar()
            return {'total_payments_amount': total_amount or 0.0}, 200
