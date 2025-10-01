## service layer of the API
from sqlalchemy_filters import apply_pagination, apply_sort
import sqlalchemy as sql
from app.common.enum import OrderStatusEnum
from app.common.error_handling import ResourceNotFoundError
from app.supplier.model import Supplier
from app.utilities.common_utils import change_string_to_time, debug_return
from config import BaseConfig, Config
from .model import Order
from app.common import filters_serialization
from app.common.queries import create_sorters, filter_and_sort_query
from app.utilities.request_utils import not_exisit_in_request
from datetime import datetime, timezone
import uuid
from app.utilities.db_utils import session_scope
from app.utilities.error_utils import handle_errors  # Import the decorator

class OrderService:
    def get_order_model(self, orders):
        result = []
        if isinstance(orders, list):
            for order in orders:
                result.append(
                    {'order': order.Order.json(),
                     'supplier': order.Supplier.json() if order.Supplier else None}
                )
            return result
        else:
            return {'order': orders.Order.json(), 'supplier': orders.Supplier.json() if orders.Supplier else None}

    @handle_errors("Order")
    def get_orders(self, id, filter): 
        with session_scope() as session:
            query = session.query(Order, Supplier).filter(Order.supplier_id == Supplier.id)
            result = None
            if id is None:
                if filter.sort is None:
                    filter.sorters = create_sorters('modified_date', 'desc')
                query = filter_and_sort_query(filter.filters, filter.sorters, query, [Order, Supplier])
                query, pagination = apply_pagination(query, page_number=int(filter.page), page_size=int(filter.per_page))
                orders = query.all()
                result = {
                    'orders': self.get_order_model(orders),
                    'filters': filters_serialization.get_pagination_serialization(pagination, filter.sort, filter.sort_order, filter.queries)
                }
            else:
                orders = query.filter(Order.id == id).first()
                if orders is None:
                    raise ResourceNotFoundError("Order")
                result = {'orders': self.get_order_model(orders)}
            return result, 200

    @handle_errors("Order")
    def create_order(self, data):
        with session_scope() as session:
            order_id = uuid.uuid4()
            # Safely handle missing expected_delivery and convert to date
            #expected_delivery = None
            #if 'expected_delivery' in data and data['expected_delivery']:
            #    dt = change_string_to_time(data['expected_delivery'])
            #    expected_delivery = dt.date() if dt else None
            # Convert string date to date object
            expected_delivery_str = data.get("expected_delivery")
            if expected_delivery_str:
                expected_delivery = datetime.strptime(expected_delivery_str, "%Y-%m-%d").date()
            else:
                expected_delivery = None
            # If 'order_date' is coming from JSON or external source:
            if isinstance(data["order_date"], str):
                data["order_date"] = datetime.strptime(data["order_date"], "%Y-%m-%d").date()

            order = Order(
                id=order_id,
                order_date=not_exisit_in_request(data, 'order_date', datetime.now(timezone.utc)),
                expected_delivery=expected_delivery,
                #expected_delivery= change_string_to_time(data['expected_delivery']),
                status=not_exisit_in_request(data, 'status', OrderStatusEnum.PENDING),
                total_amount=not_exisit_in_request(data, 'total_amount', 0.000),
                #currency=not_exisit_in_request(data, 'currency', 'USD'),
                #payment_terms=not_exisit_in_request(data, 'payment_terms', None),
                notes=not_exisit_in_request(data, 'notes', None),
                supplier_id=not_exisit_in_request(data, 'supplier_id', None),
                create_date=datetime.now(timezone.utc),
                modified_date=datetime.now(timezone.utc)
            )

            session.add(order)
            session.commit()

            return 'Order Created', 201

    @handle_errors("Order")
    def update_order(self, id, data):
        with session_scope() as session:
            order = session.query(Order).filter_by(id=id).first()
            if order is None:
                raise ResourceNotFoundError("Order")

            order.order_date = not_exisit_in_request(data, 'order_date', order.order_date)
            order.expected_delivery = not_exisit_in_request(data, 'expected_delivery', order.expected_delivery)
            order.status = not_exisit_in_request(data, 'status', order.status)
            order.total_amount = not_exisit_in_request(data, 'total_amount', order.total_amount)
            order.currency = not_exisit_in_request(data, 'currency', order.currency)
            order.payment_terms = not_exisit_in_request(data, 'payment_terms', order.payment_terms)
            order.notes = not_exisit_in_request(data, 'notes', order.notes)
            order.supplier_id = not_exisit_in_request(data, 'supplier_id', order.supplier_id)

            order.modified_date = datetime.now(timezone.utc)
            session.commit()

            return 'Updated', 200

    @handle_errors("Order")
    def delete_order(self, id):
        with session_scope() as session:
            order = session.query(Order).filter_by(id=id).first()

            if order is None:
                raise ResourceNotFoundError("Order")

            session.delete(order)
            session.commit()

            return 'Order deleted', 200

    @handle_errors("Order")
    def get_total_orders_count(self, filter=None):
        with session_scope() as session:
            query = session.query(sql.func.count(Order.id))
            if filter:
                query = filter_and_sort_query(filter.filters, [], query, Order)
            total_count = query.scalar()
            return {'total_orders_count': total_count or 0}, 200

    @handle_errors("Order")
    def get_total_orders_amount(self, filter=None):
        with session_scope() as session:
            query = session.query(sql.func.sum(Order.total_amount))
            if filter:
                query = filter_and_sort_query(filter.filters, [], query, Order)
            total_amount = query.scalar()
            return {'total_orders_amount': float(total_amount or 0)}, 200

